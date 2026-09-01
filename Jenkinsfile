pipeline {

    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        PYTHONIOENCODING = 'utf-8'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Setup') {
            steps {
                bat 'python -m venv venv'

                bat '''
                venv\\Scripts\\python -m pip install -r requirements.txt
                '''
            }
        }

        stage('AWS Authentication') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-driftguard',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    bat '''
                    venv\\Scripts\\python -c "import boto3; print(boto3.client('sts', region_name='ap-south-1').get_caller_identity()['Arn'])"
                    '''
                }
            }
        }

        stage('Drift Detection') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-driftguard',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    bat '''
                    venv\\Scripts\\python detector\\drift_detector.py
                    '''
                }
            }
        }

        stage('Risk Analysis') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-driftguard',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    bat '''
                    venv\\Scripts\\python detector\\risk_engine.py
                    '''
                }
            }
        }

        stage('Email Alert') {
            steps {

                script {

                    def result = bat(
                        script: '''
                        @echo off
                        venv\\Scripts\\python -c "import json; r=json.load(open('reports/drift_report.json')); print(r['status']); print(r['risk']['level']); print(r['risk']['score'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    /*
                     * Remove empty lines so Windows BAT output
                     * does not break the parsing.
                     */
                    def lines = result
                        .readLines()
                        .findAll { it?.trim() }

                    def status = lines[-3].trim()
                    def riskLevel = lines[-2].trim()
                    def riskScore = lines[-1].trim()

                    echo "Drift Status: ${status}"
                    echo "Risk Level: ${riskLevel}"
                    echo "Risk Score: ${riskScore}"


                    /*
                     * Send email ONLY when drift is detected.
                     */
                    if (status == 'DRIFT_DETECTED') {

                        try {

                            emailext(

                                to: 'guru08092004ff@gmail.com',

                                from: 'guru08092004ff@gmail.com',

                                subject: "DriftGuard ALERT - ${riskLevel} Risk - Build #${env.BUILD_NUMBER}",

                                mimeType: 'text/html',

                                body: """
                                <html>

                                <body>

                                <h2>DriftGuard Security Alert</h2>

                                <p>
                                <b>Status:</b>
                                ${status}
                                </p>

                                <p>
                                <b>Risk Level:</b>
                                ${riskLevel}
                                </p>

                                <p>
                                <b>Risk Score:</b>
                                ${riskScore}
                                </p>

                                <hr>

                                <h3>
                                Unauthorized Infrastructure Change Detected
                                </h3>

                                <p>
                                DriftGuard detected an unauthorized
                                change in the AWS infrastructure.
                                </p>

                                <p>
                                <b>Jenkins Build:</b>
                                #${env.BUILD_NUMBER}
                                </p>

                                <p>
                                Please review the infrastructure
                                change before allowing the pipeline
                                to continue.
                                </p>

                                <hr>

                                <p>
                                <b>
                                DriftGuard CI/CD Security Pipeline
                                </b>
                                </p>

                                </body>

                                </html>
                                """
                            )

                            echo '========================================='
                            echo '🚨 DRIFT DETECTED'
                            echo '📧 Email alert sent successfully.'
                            echo '========================================='

                        }

                        catch (Exception e) {

                            echo '========================================='
                            echo '⚠️ Email sending failed'
                            echo "Error: ${e.getMessage()}"
                            echo '========================================='

                            /*
                             * Email failure should NOT hide
                             * the actual security drift.
                             *
                             * Security Gate will handle the failure.
                             */
                        }

                    }

                    else {

                        echo '========================================='
                        echo '✅ NO DRIFT DETECTED'
                        echo '📧 Email alert skipped.'
                        echo '========================================='
                    }
                }
            }
        }

        stage('Security Gate') {
            steps {

                bat '''
                venv\\Scripts\\python -c "import json,sys; r=json.load(open('reports/drift_report.json')); print('Security Gate: '+r['status']); print('Risk Level: '+r['risk']['level']); print('Risk Score: '+str(r['risk']['score'])); sys.exit(1 if r['status']=='DRIFT_DETECTED' else 0)"
                '''
            }
        }
    }

    post {

        always {

            archiveArtifacts artifacts: 'reports/drift_report.json',
                             allowEmptyArchive: true

            echo '========================================='
            echo 'DriftGuard pipeline execution completed.'
            echo '========================================='
        }
    }
}