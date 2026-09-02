pipeline {

    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        PYTHONIOENCODING   = 'utf-8'

        EMAIL_TO   = 'guru08092004ff@gmail.com'
        EMAIL_FROM = 'guru08092004ff@gmail.com'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Setup') {
            steps {
                bat '''
                    if not exist venv (
                        python -m venv venv
                    )

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
                        venv\\Scripts\\python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Arn'])"
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
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def level = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['level'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def score = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['score'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def reason = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['reason'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "========================================"
                    echo "      DRIFTGUARD RISK ANALYSIS"
                    echo "========================================"
                    echo "Status      : ${status}"
                    echo "Risk Level  : ${level}"
                    echo "Risk Score  : ${score}"
                    echo "Reason      : ${reason}"
                    echo "========================================"
                }
            }
        }

        stage('Email Alert') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    if (status == 'DRIFT_DETECTED') {

                        def level = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['level'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def score = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['score'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        try {

                            emailext(
                                to: "${EMAIL_TO}",
                                from: "${EMAIL_FROM}",
                                subject: "🚨 DriftGuard Alert - ${level} Risk",
                                mimeType: 'text/html',
                                body: """
                                <html>
                                <body>

                                <h2>🚨 DriftGuard Security Alert</h2>

                                <table border="1" cellpadding="10">

                                <tr>
                                <td>Status</td>
                                <td><b>${status}</b></td>
                                </tr>

                                <tr>
                                <td>Risk Level</td>
                                <td><b>${level}</b></td>
                                </tr>

                                <tr>
                                <td>Risk Score</td>
                                <td><b>${score}</b></td>
                                </tr>

                                <tr>
                                <td>Resource</td>
                                <td>driftguard-web-sg</td>
                                </tr>

                                <tr>
                                <td>Region</td>
                                <td>ap-south-1</td>
                                </tr>

                                <tr>
                                <td>Build</td>
                                <td>#${BUILD_NUMBER}</td>
                                </tr>

                                </table>

                                <br>

                                Unauthorized public inbound access detected.

                                </body>
                                </html>
                                """
                            )

                            echo "Email alert submitted."

                        } catch(Exception e) {

                            echo "Email failed but pipeline continues."
                        }

                    } else {

                        echo "NO_DRIFT - Email skipped."
                    }
                }
            }
        }

        stage('Discord Alert') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    if(status == 'DRIFT_DETECTED') {

                        def level = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['level'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def score = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['score'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        withCredentials([
                            string(
                                credentialsId: 'discord-webhook',
                                variable: 'DISCORD_WEBHOOK'
                            )
                        ]) {

                            def message = """🚨 DRIFTGUARD SECURITY ALERT

Status: DRIFT DETECTED

Resource: driftguard-web-sg
Region: ap-south-1

Risk Level: ${level}
Risk Score: ${score}

Reason:
Public inbound access detected

Jenkins Build #${BUILD_NUMBER}

🔴 Security Gate blocked this build."""

                            writeFile(
                                file: 'discord.json',
                                text: groovy.json.JsonOutput.toJson([
                                    content: message
                                ])
                            )

                            bat '''
                                @curl -s -X POST ^
                                -H "Content-Type: application/json" ^
                                --data-binary "@discord.json" ^
                                "%DISCORD_WEBHOOK%"
                            '''
                        }

                        echo "Discord alert sent successfully."

                    } else {

                        echo "NO_DRIFT - Discord skipped."
                    }
                }
            }
        }

        stage('Security Gate') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def level = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['level'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def score = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json;d=json.load(open('reports/drift_report.json'));print(d['risk']['score'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "========================================"
                    echo "         SECURITY GATE"
                    echo "========================================"
                    echo "Status      : ${status}"
                    echo "Risk Level  : ${level}"
                    echo "Risk Score  : ${score}"
                    echo "========================================"

                    if(status == 'DRIFT_DETECTED') {

                        error("SECURITY GATE BLOCKED BUILD - ${level} Risk (${score})")

                    } else {

                        echo "Security Gate PASSED"
                    }
                }
            }
        }
    }

    post {

        always {

            archiveArtifacts artifacts: 'reports/drift_report.json',
                             allowEmptyArchive: true

            bat '''
                if exist discord.json del /f /q discord.json
            '''

            echo "DriftGuard pipeline execution completed."
        }

        success {

            echo "BUILD SUCCESS"
        }

        failure {

            echo "BUILD BLOCKED DUE TO DRIFT"
        }
    }
}