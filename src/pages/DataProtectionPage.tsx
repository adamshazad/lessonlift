import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const DataProtectionPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />

      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Data Protection
          </h1>
          <p className="text-gray-600 mb-8">
            Last updated: January 2025
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Our Commitment to Data Protection</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                At LessonLift, we take data protection seriously. We are committed to protecting your personal data
                and respecting your privacy in accordance with UK data protection laws, including the UK GDPR and
                the Data Protection Act 2018.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                This page explains how we protect your data, your rights under data protection law, and how to
                exercise those rights.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Data Protection Principles</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We process your personal data in accordance with the following principles:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li><strong>Lawfulness, fairness and transparency:</strong> We process data lawfully, fairly, and in a transparent manner</li>
                <li><strong>Purpose limitation:</strong> We collect data for specified, explicit, and legitimate purposes only</li>
                <li><strong>Data minimization:</strong> We only collect data that is adequate, relevant, and necessary</li>
                <li><strong>Accuracy:</strong> We keep personal data accurate and up to date</li>
                <li><strong>Storage limitation:</strong> We keep personal data only as long as necessary</li>
                <li><strong>Integrity and confidentiality:</strong> We protect data against unauthorized processing, loss, or damage</li>
                <li><strong>Accountability:</strong> We take responsibility for compliance with data protection principles</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Legal Basis for Processing</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We process your personal data under the following legal bases:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li><strong>Contract:</strong> Processing necessary to provide our services to you</li>
                <li><strong>Legitimate interests:</strong> Processing necessary for our legitimate business interests, such as improving our services</li>
                <li><strong>Consent:</strong> Where you have given clear consent for us to process your data for specific purposes</li>
                <li><strong>Legal obligation:</strong> Processing necessary to comply with legal requirements</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Your Data Protection Rights</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Under UK data protection law, you have the following rights:
              </p>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Access</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to request copies of your personal data. We may charge a reasonable fee for
                    additional copies if your request is clearly unfounded or excessive.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Rectification</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to request that we correct any information you believe is inaccurate or
                    complete information you believe is incomplete.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Erasure</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to request that we erase your personal data, under certain conditions, such
                    as when the data is no longer necessary for the purposes it was collected.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Restrict Processing</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to request that we restrict the processing of your personal data, under
                    certain conditions, such as when you contest the accuracy of the data.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Object</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to object to our processing of your personal data, under certain conditions,
                    particularly when we process data based on legitimate interests.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Data Portability</h3>
                  <p className="text-gray-700 leading-relaxed">
                    You have the right to request that we transfer the data we have collected to another organization,
                    or directly to you, under certain conditions.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Right to Withdraw Consent</h3>
                  <p className="text-gray-700 leading-relaxed">
                    Where we process your data based on your consent, you have the right to withdraw that consent
                    at any time. This will not affect the lawfulness of processing before the withdrawal.
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. How to Exercise Your Rights</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                To exercise any of your data protection rights, please contact us at:
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Email: lessonliftapp@gmail.com<br />
                Address: London, United Kingdom
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                We will respond to your request within one month of receipt. In some cases, we may need to extend
                this period by a further two months if your request is complex or we receive multiple requests.
                We will inform you of any such extension and explain the reasons for the delay.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Security Measures</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We implement appropriate technical and organizational measures to protect your personal data, including:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>Encryption of data in transit and at rest</li>
                <li>Regular security assessments and audits</li>
                <li>Access controls and authentication measures</li>
                <li>Employee training on data protection practices</li>
                <li>Regular backups and disaster recovery procedures</li>
                <li>Secure data centers with physical security controls</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Breach Notification</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                In the event of a personal data breach that is likely to result in a risk to your rights and freedoms,
                we will notify you and the Information Commissioner's Office (ICO) without undue delay and, where
                feasible, within 72 hours of becoming aware of the breach.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. International Data Transfers</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                While we primarily store and process data within the UK and European Economic Area (EEA), we may
                transfer your personal data to third-party service providers in other countries. When we do so,
                we ensure appropriate safeguards are in place, such as:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>Standard contractual clauses approved by the UK authorities</li>
                <li>Adequacy decisions recognizing equivalent data protection standards</li>
                <li>Binding corporate rules for intra-group transfers</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                LessonLift is designed for use by teachers and educational professionals. We do not knowingly collect
                personal data from children under 13. If you are a parent or guardian and believe we may have collected
                information from a child, please contact us immediately.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Data Protection Officer</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have questions about our data protection practices or wish to make a complaint, you can contact
                our data protection team at lessonliftapp@gmail.com.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Supervisory Authority</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You have the right to lodge a complaint with the Information Commissioner's Office (ICO), the UK's
                supervisory authority for data protection:
              </p>
              <p className="text-gray-700 leading-relaxed">
                Information Commissioner's Office<br />
                Wycliffe House, Water Lane<br />
                Wilmslow, Cheshire<br />
                SK9 5AF<br />
                <br />
                Helpline: 0303 123 1113<br />
                Website: www.ico.org.uk
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Updates to This Policy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may update this Data Protection page from time to time to reflect changes in our practices or
                legal requirements. We will notify you of any significant changes by posting a notice on our website
                or by contacting you directly.
              </p>
            </section>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default DataProtectionPage;
