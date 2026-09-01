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
                bat 'venv\\Scripts\\python -m pip install -r requirements.txt'
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

                    def lines = result.readLines()

                    def status = lines[-3]
                    def riskLevel = lines[-2]
                    def riskScore = lines[-1]

                    echo "Drift Status: ${status}"
                    echo "Risk Level: ${riskLevel}"
                    echo "Risk Score: ${riskScore}"

                    if (status == 'DRIFT_DETECTED') {

                        emailext(
                            to: 'guru08092004ff@gmail.com',
                            subject: "🚨 DriftGuard Alert - ${riskLevel} Risk",
                            mimeType: 'text/html',
                            body: """
                                <html>
                                <body>

                                <h2>🚨 DriftGuard Security Alert</h2>

                                <p><b>Status:</b> ${status}</p>
                                <p><b>Risk Level:</b> ${riskLevel}</p>
                                <p><b>Risk Score:</b> ${riskScore}</p>

                                <hr>

                                <h3>Unauthorized Infrastructure Change Detected</h3>

                                <p>
                                DriftGuard detected an unauthorized change
                                in the AWS infrastructure.
                                </p>

                                <p>
                                <b>Jenkins Build:</b> #${env.BUILD_NUMBER}
                                </p>

                                <p>
                                Please review the attached
                                <b>drift_report.json</b>.
                                </p>

                                <hr>

                                <p>
                                <b>DriftGuard CI/CD Security Pipeline</b>
                                </p>

                                </body>
                                </html>
                            """,
                            attachmentsPattern: 'reports/drift_report.json'
                        )

                        echo '🚨 Drift detected - Email alert sent successfully.'

                    } else {

                        echo '✅ No drift detected - Email alert skipped.'

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

            echo 'DriftGuard pipeline execution completed.'
        }
    }
}