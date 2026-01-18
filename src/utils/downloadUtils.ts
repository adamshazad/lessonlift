export function downloadAsText(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadAsPDF(htmlContent: string, filename: string): void {
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;

  const styles = `
    <style>
      @media print {
        body {
          font-family: Arial, sans-serif;
          padding: 20px;
          color: #000;
        }
        .lesson-header {
          margin-bottom: 20px;
          border-bottom: 2px solid #4CAF50;
          padding-bottom: 10px;
        }
        .lesson-header h1 {
          color: #4CAF50;
          font-size: 24px;
          margin: 0 0 10px 0;
        }
        .lesson-meta {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
          font-size: 14px;
        }
        .meta-item {
          color: #666;
        }
        .lesson-content {
          margin-top: 20px;
        }
        .section-heading {
          color: #2c5f2d;
          margin-top: 20px;
          margin-bottom: 10px;
          font-size: 18px;
        }
        .subsection {
          color: #4CAF50;
          margin-top: 15px;
          margin-bottom: 8px;
          font-size: 16px;
        }
        li {
          margin-bottom: 5px;
          line-height: 1.6;
        }
        .nested-item {
          margin-left: 20px;
        }
        p {
          line-height: 1.6;
          margin-bottom: 10px;
        }
      }
    </style>
  `;

  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>${filename}</title>
        ${styles}
      </head>
      <body>
        ${htmlContent}
      </body>
    </html>
  `);

  printWindow.document.close();

  setTimeout(() => {
    printWindow.print();
    setTimeout(() => printWindow.close(), 1000);
  }, 500);
}

export function downloadAsDOCX(htmlContent: string, filename: string): void {
  const header = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office'
          xmlns:w='urn:schemas-microsoft-com:office:word'
          xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
      <meta charset='utf-8'>
      <title>${filename}</title>
      <style>
        body { font-family: Calibri, Arial, sans-serif; font-size: 11pt; }
        h1 { color: #4CAF50; font-size: 20pt; }
        h2 { color: #2c5f2d; font-size: 16pt; margin-top: 12pt; }
        h3 { color: #2c5f2d; font-size: 14pt; margin-top: 10pt; }
        h4 { color: #4CAF50; font-size: 12pt; margin-top: 8pt; }
        p { margin-bottom: 6pt; line-height: 1.5; }
        li { margin-bottom: 4pt; line-height: 1.5; }
        .lesson-meta { font-size: 10pt; color: #666666; margin-bottom: 12pt; }
      </style>
    </head>
    <body>
  `;

  const footer = '</body></html>';
  const fullContent = header + htmlContent + footer;

  const blob = new Blob(['\ufeff', fullContent], { type: 'application/msword' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.doc`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function sanitizeFilename(subject: string, topic: string): string {
  const combined = `${subject}_${topic}`;
  return combined
    .replace(/[^a-z0-9]/gi, '_')
    .replace(/_+/g, '_')
    .toLowerCase();
}
