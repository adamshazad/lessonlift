import { createClient } from 'npm:@supabase/supabase-js@2.57.4';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
};

interface LessonRequest {
  yearGroup: string;
  abilityLevel: string;
  lessonDuration: number;
  subject: string;
  topic: string;
  learningObjective?: string;
  senEalNotes?: string;
  regenerationInstruction?: string;
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const openaiKey = Deno.env.get('OPENAI_API_KEY');

    if (!openaiKey) {
      throw new Error('OpenAI API key not configured. Please add OPENAI_API_KEY to your Supabase Edge Function secrets.');
    }

    const authHeader = req.headers.get('Authorization')!;
    if (!authHeader) {
      throw new Error('Missing authorization header');
    }

    const token = authHeader.replace('Bearer ', '');
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data: { user }, error: userError } = await supabase.auth.getUser(token);
    if (userError || !user) {
      console.error('Auth error:', userError);
      return new Response(
        JSON.stringify({
          success: false,
          error: 'Authentication failed. Please log in again.',
        }),
        {
          status: 401,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      );
    }

    // Check trial status and limits
    // Free Trial: 5 total lessons, 7 days from first use
    // Paid Plans:
    // - Starter: 1/day, 30/month, PDF only
    // - Standard: 3/day, 90/month, PDF + DOCX
    // - Pro: 5/day, 150/month, PDF + DOCX + TXT
    const { data: limitCheck, error: limitError } = await supabase.rpc(
      'check_and_increment_daily_count',
      { p_user_id: user.id }
    );

    if (limitError) {
      console.error('Error checking limits:', limitError);
      throw new Error('Failed to check lesson limits');
    }

    // If limit reached (trial expired, daily, or monthly), return error with details
    if (!limitCheck.allowed) {
      const response: any = {
        success: false,
        error: limitCheck.message,
        limitReached: true,
        isTrial: limitCheck.is_trial,
      };

      // Add trial-specific fields
      if (limitCheck.is_trial) {
        response.trialExpired = true;
        response.expiredBy = limitCheck.expired_by;
        response.lessonsUsed = limitCheck.lessons_used;
      } else {
        // Add paid plan limit fields
        response.limitType = limitCheck.limit_type;
        response.currentCount = limitCheck.current_count;
        response.maxCount = limitCheck.max_count;
        response.plan = limitCheck.plan;
        response.monthlyCount = limitCheck.monthly_current;
        response.monthlyMax = limitCheck.monthly_max;
      }

      return new Response(
        JSON.stringify(response),
        {
          status: 429,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      );
    }

    const lessonRequest: LessonRequest = await req.json();

    const minWords = getMinWordCount(lessonRequest.lessonDuration);
    let lessonContent = '';
    let attempts = 0;
    const maxAttempts = 3;

    while (attempts < maxAttempts) {
      attempts++;
      const isRetry = attempts > 1;
      const prompt = buildLessonPrompt(lessonRequest, isRetry);
      lessonContent = await generateLessonWithOpenAI(prompt, openaiKey);

      const wordCount = countWords(lessonContent);

      if (wordCount >= minWords) {
        break;
      }

      if (attempts === maxAttempts) {
        break;
      }
    }

    const lessonHtml = formatLessonAsHtml(lessonContent, lessonRequest);
    const lessonText = formatLessonAsText(lessonContent, lessonRequest);

    const { data: lesson, error: insertError } = await supabase
      .from('lessons')
      .insert({
        user_id: user.id,
        year_group: lessonRequest.yearGroup,
        ability_level: lessonRequest.abilityLevel,
        lesson_duration: lessonRequest.lessonDuration,
        subject: lessonRequest.subject,
        topic: lessonRequest.topic,
        learning_objective: lessonRequest.learningObjective,
        sen_eal_notes: lessonRequest.senEalNotes,
        regeneration_instruction: lessonRequest.regenerationInstruction,
        lesson_content: lessonHtml,
        lesson_text: lessonText,
      })
      .select()
      .single();

    if (insertError) {
      throw insertError;
    }

    // Build response with usage info
    const response: any = {
      success: true,
      lesson: {
        id: lesson.id,
        html: lessonHtml,
        text: lessonText,
        ...lessonRequest,
      },
    };

    // Add trial or paid plan usage info
    if (limitCheck.is_trial) {
      response.usage = {
        isTrial: true,
        lessonsUsed: limitCheck.lessons_used,
        lessonsRemaining: limitCheck.lessons_remaining,
      };
    } else {
      response.usage = {
        isTrial: false,
        dailyCount: limitCheck.current_count,
        dailyMax: limitCheck.max_count,
        dailyRemaining: limitCheck.remaining,
        monthlyCount: limitCheck.monthly_current,
        monthlyMax: limitCheck.monthly_max,
        monthlyRemaining: limitCheck.monthly_remaining,
        plan: limitCheck.plan,
      };
    }

    return new Response(
      JSON.stringify(response),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Edge function error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message || 'An unexpected error occurred',
      }),
      {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
});

function getMinWordCount(duration: number): number {
  if (duration === 30) return 750;
  if (duration === 45) return 850;
  if (duration === 60) return 1000;
  return 750;
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).length;
}

function buildLessonPrompt(request: LessonRequest, isRetry: boolean = false): string {
  const minWords = getMinWordCount(request.lessonDuration);

  let prompt = `You are an expert UK classroom teacher and lesson designer.
Generate a classroom-ready UK lesson plan that would confidently score at least 8/10 in a professional review.

LESSON DETAILS:
Year Group: ${request.yearGroup}
Subject: ${request.subject}
Topic: ${request.topic}
Ability Level: ${request.abilityLevel}
Lesson Duration: ${request.lessonDuration} minutes
Learning Objective: ${request.learningObjective || 'Not specified'}
SEN/EAL Notes: ${request.senEalNotes || 'None'}

STRICT RULES:
• Match the Year Group and Ability precisely
• Teach 1 core concept for lower ability, up to 2 linked concepts for mixed/higher
• Avoid cognitive overload and unnecessary theory
• Prioritise clarity, modelling, and scaffolding
• Use British English only (analyse, organise, colour, etc.)
• Minimum ${minWords} words, maximum ${minWords + 300} words
• Bold all section headings with **heading** format
• Include timing estimates that are realistic (must total ${request.lessonDuration} mins)

MANDATORY STRUCTURE:

**1. Lesson Overview**
Subject, topic, year group, ability, duration

**2. Key Vocabulary**
Present as a table with two columns:
| Tier 2 (Academic) | Tier 3 (Technical) |
| [word] | [word] |
| [word] | [word] |
| [word] | [word] |

- Tier 2: Cross-curricular academic vocabulary (e.g., analyse, demonstrate, compare)
- Tier 3: Subject-specific technical terms (e.g., photosynthesis, multiplication, adjective)
- Include exactly 3 words in each column
- Make vocabulary age-appropriate for the year group

**3. Learning Objective & Success Criteria**
- Clear, measurable objective aligned to the ability level
- 3-4 specific success criteria that can be observed

**4. Retrieval Starter** (5 minutes)
- 2-3 questions that activate prior knowledge needed for today's learning
- Include model answers immediately after the questions

**5. Main Teaching** (appropriate timing)
- Step-by-step explanation with explicit modelling
- Use "I Do" approach - show exactly what to do
- Reference specific examples and teacher dialogue where helpful
- Use visuals, manipulatives, or diagrams where appropriate
- Bold vocabulary words when first introduced and defined

**6. Guided Practice** (appropriate timing)
- "We Do" together activities
- Teacher-led examples with student participation
- Check for understanding throughout

**7. Independent / Supported Practice** (appropriate timing)
- "You Do" activities closely aligned to success criteria
- Scaffolded appropriately for the stated ability level
- Specific task instructions

**8. Justification Plenary** (5 minutes)
- 2-3 "How do you know?" or "Why?" questions (NOT simple summaries)
- Include model answers showing expected reasoning
- Examples: "Why does X belong in this category?", "How do you know this is correct?"

**9. Differentiation**
- **Scaffold:** Specific sentence starters, worked examples, or visual aids
- **Extension:** Deeper "Why?" or "What if?" questions (not just harder language)
- Must be content-specific to this lesson

**10. Assessment & Evidence**
- How learning will be checked during the lesson
- What observable evidence shows success criteria are met

**11. Resources**
- Complete, realistic list of materials needed

**12. Safety & Risk Assessment**
- If equipment/materials are used: List 3 specific safety points (hazard + control measure)
- If paper-based only: State "No specific safety concerns. Standard classroom expectations apply."

QUALITY CHECKS:
• Is this lesson realistic and teachable within ${request.lessonDuration} minutes?
• Does it avoid cognitive overload for the stated ability?
• Are instructions clear enough for immediate classroom use?
• Is there a logical flow from retrieval → teaching → practice → assessment?`;

  if (request.regenerationInstruction) {
    prompt += `\n\nSPECIAL INSTRUCTION: ${request.regenerationInstruction}`;
  }

  if (isRetry) {
    prompt += `\n\nCRITICAL: The previous response was too short. You MUST:
- Include ALL mandatory sections in order
- Reach the ${minWords} word minimum (maximum ${minWords + 300})
- Provide detailed, step-by-step content in each section
- Include complete model answers for retrieval and plenary questions
- Ensure vocabulary table is properly formatted
- Add specific scaffolds and extensions`;
  }

  return prompt;
}

async function generateLessonWithOpenAI(prompt: string, apiKey: string): Promise<string> {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are an expert UK classroom teacher and lesson designer. Generate classroom-ready lesson plans that score 8/10+ in professional reviews. Prioritise clarity, realistic pacing, and practical teachability. Use British English. Follow the exact structure provided: Lesson Overview, Key Vocabulary (table format with Tier 2 and Tier 3), Learning Objective & Success Criteria, Retrieval Starter, Main Teaching (with I Do modelling), Guided Practice (We Do), Independent Practice (You Do), Justification Plenary (reasoning questions, not summaries), Differentiation (specific scaffolds and extensions), Assessment & Evidence, Resources, and Safety notes. Bold vocabulary words when defined. Include model answers for all questions. Avoid cognitive overload - teach 1 concept thoroughly rather than rushing multiple topics. All activities must be subject-specific and directly relevant.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.25,
      max_tokens: 2200,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI API error: ${error}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

function formatLessonAsHtml(content: string, request: LessonRequest): string {
  const lines = content.split('\n');
  let html = `<div class="lesson-plan">`;

  html += `<div class="lesson-header">`;
  html += `<h1>${request.subject}: ${request.topic}</h1>`;
  html += `<div class="lesson-meta">`;
  html += `<span class="meta-item"><strong>Year Group:</strong> ${request.yearGroup}</span>`;
  html += `<span class="meta-item"><strong>Ability:</strong> ${request.abilityLevel}</span>`;
  html += `<span class="meta-item"><strong>Duration:</strong> ${request.lessonDuration} minutes</span>`;
  html += `</div>`;
  html += `</div>`;

  html += `<style>
    .vocab-table {
      width: 100%;
      max-width: 600px;
      margin: 20px 0;
      border-collapse: collapse;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      border-radius: 8px;
      overflow: hidden;
    }
    .vocab-table th {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 16px;
      text-align: left;
      font-weight: 600;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .vocab-table td {
      padding: 14px 16px;
      border-bottom: 1px solid #e5e7eb;
      background: white;
      font-size: 15px;
    }
    .vocab-table tr:last-child td {
      border-bottom: none;
    }
    .vocab-table tr:hover td {
      background: #f9fafb;
    }
  </style>`;

  html += `<div class="lesson-content">`;

  let inList = false;
  let inTable = false;
  let tableRows: string[][] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (!line) {
      if (inList) {
        html += `</ul>`;
        inList = false;
      }
      if (inTable) {
        html += formatTable(tableRows);
        inTable = false;
        tableRows = [];
      }
      continue;
    }

    if (line.startsWith('|') && line.endsWith('|')) {
      if (line.includes('---')) {
        continue;
      }

      if (inList) {
        html += `</ul>`;
        inList = false;
      }

      inTable = true;
      const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
      tableRows.push(cells);
      continue;
    }

    if (inTable) {
      html += formatTable(tableRows);
      inTable = false;
      tableRows = [];
    }

    if (line.match(/^\*\*.*\*\*$/)) {
      if (inList) {
        html += `</ul>`;
        inList = false;
      }
      const heading = line.replace(/^\*\*/, '').replace(/\*\*$/, '');
      html += `<h2 class="section-heading">${heading}</h2>`;
    } else if (line.startsWith('- ') || line.startsWith('• ')) {
      if (!inList) {
        html += `<ul>`;
        inList = true;
      }
      const text = line.replace(/^[-•]\s*/, '');
      html += `<li>${text}</li>`;
    } else {
      if (inList) {
        html += `</ul>`;
        inList = false;
      }
      const processedLine = line.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      html += `<p>${processedLine}</p>`;
    }
  }

  if (inList) {
    html += `</ul>`;
  }
  if (inTable) {
    html += formatTable(tableRows);
  }

  html += `</div></div>`;

  return html;
}

function formatTable(rows: string[][]): string {
  if (rows.length === 0) return '';

  let html = `<table class="vocab-table">`;

  html += `<thead><tr>`;
  for (const cell of rows[0]) {
    html += `<th>${cell}</th>`;
  }
  html += `</tr></thead>`;

  html += `<tbody>`;
  for (let i = 1; i < rows.length; i++) {
    html += `<tr>`;
    for (const cell of rows[i]) {
      html += `<td>${cell}</td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody>`;

  html += `</table>`;
  return html;
}

function formatLessonAsText(content: string, request: LessonRequest): string {
  let text = `========================================\n`;
  text += `LESSON PLAN\n`;
  text += `========================================\n\n`;
  text += `Subject: ${request.subject}\n`;
  text += `Topic: ${request.topic}\n`;
  text += `Year Group: ${request.yearGroup}\n`;
  text += `Ability Level: ${request.abilityLevel}\n`;
  text += `Duration: ${request.lessonDuration} minutes\n\n`;

  if (request.learningObjective) {
    text += `Learning Objective: ${request.learningObjective}\n\n`;
  }

  if (request.senEalNotes) {
    text += `SEN/EAL Notes: ${request.senEalNotes}\n\n`;
  }

  text += `========================================\n\n`;
  text += content;
  text += `\n\n========================================\n`;
  text += `Generated by LessonLift\n`;
  text += `========================================\n`;

  return text;
}
