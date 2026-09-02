pipeline {

    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        PYTHONIOENCODING   = 'utf-8'

        EMAIL_TO   = 'guruvasanth097@gmail.com'
        EMAIL_FROM = 'guruvasanth097@gmail.com'
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

                    venv\\Scripts\\python -m pip install --upgrade pip
                    venv\\Scripts\\pip install -r requirements.txt
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

                    def reportStatus = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('status','UNKNOWN'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskLevel = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_level','LOW'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskScore = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_score',0))"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "========================================"
                    echo "        DRIFTGUARD RISK ANALYSIS"
                    echo "========================================"
                    echo "Drift Status : ${reportStatus}"
                    echo "Risk Level   : ${riskLevel}"
                    echo "Risk Score   : ${riskScore}"
                    echo "========================================"
                }
            }
        }

        stage('Email Alert') {
            steps {
                script {

                    def reportStatus = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('status','UNKNOWN'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    if (reportStatus == 'DRIFT_DETECTED') {

                        def riskLevel = bat(
                            script: '''
                                venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_level','HIGH'))"
                            ''',
                            returnStdout: true
                        ).trim()

                        def riskScore = bat(
                            script: '''
                                venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_score',0))"
                            ''',
                            returnStdout: true
                        ).trim()

                        def reportText = bat(
                            script: '''
                                venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(json.dumps(d, indent=2))"
                            ''',
                            returnStdout: true
                        ).trim()

                        try {

                            emailext(
                                to: "${env.EMAIL_TO}",
                                from: "${env.EMAIL_FROM}",
                                replyTo: "${env.EMAIL_FROM}",
                                subject: "DriftGuard ALERT - ${riskLevel} Risk - Build #${env.BUILD_NUMBER}",
                                mimeType: 'text/html',
                                body: """
                                    <html>
                                    <body>

                                    <h2>🚨 DriftGuard Security Alert</h2>

                                    <p><b>Drift detected in AWS infrastructure.</b></p>

                                    <table border="1" cellpadding="8" cellspacing="0">
                                        <tr>
                                            <td><b>Build</b></td>
                                            <td>#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr>
                                            <td><b>Status</b></td>
                                            <td>DRIFT_DETECTED</td>
                                        </tr>
                                        <tr>
                                            <td><b>Risk Level</b></td>
                                            <td>${riskLevel}</td>
                                        </tr>
                                        <tr>
                                            <td><b>Risk Score</b></td>
                                            <td>${riskScore}</td>
                                        </tr>
                                    </table>

                                    <h3>Drift Report</h3>

                                    <pre>${reportText}</pre>

                                    <p>
                                        DriftGuard Security Gate blocked the deployment
                                        because unauthorized infrastructure changes were detected.
                                    </p>

                                    </body>
                                    </html>
                                """
                            )

                            echo "Email alert submitted successfully."
                            echo "Recipient: ${env.EMAIL_TO}"

                        } catch (Exception e) {

                            echo "WARNING: Email alert failed."
                            echo "Reason: ${e.getMessage()}"
                            echo "Continuing with Discord alert and Security Gate."
                        }

                    } else {

                        echo "NO_DRIFT - Email alert skipped."
                    }
                }
            }
        }

        stage('Discord Alert') {
            steps {
                script {

                    def reportStatus = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('status','UNKNOWN'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    if (reportStatus == 'DRIFT_DETECTED') {

                        def riskLevel = bat(
                            script: '''
                                venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_level','HIGH'))"
                            ''',
                            returnStdout: true
                        ).trim()

                        def riskScore = bat(
                            script: '''
                                venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_score',0))"
                            ''',
                            returnStdout: true
                        ).trim()

                        withCredentials([
                            string(
                                credentialsId: 'discord-webhook',
                                variable: 'DISCORD_WEBHOOK'
                            )
                        ]) {

                            def discordMessage = """
🚨 **DRIFTGUARD SECURITY ALERT**

**Status:** DRIFT DETECTED
**Resource:** driftguard-web-sg
**Region:** ap-south-1
**Risk Level:** ${riskLevel}
**Risk Score:** ${riskScore}
**Jenkins Build:** #${env.BUILD_NUMBER}

Unauthorized infrastructure changes were detected.

🔴 Security Gate will block this build.
"""

                            writeFile(
                                file: 'discord_payload.json',
                                text: groovy.json.JsonOutput.toJson([
                                    content: discordMessage
                                ])
                            )

                            bat '''
                                curl -s -X POST ^
                                -H "Content-Type: application/json" ^
                                --data-binary "@discord_payload.json" ^
                                "%DISCORD_WEBHOOK%"
                            '''
                        }

                        echo "Discord alert sent successfully."

                    } else {

                        echo "NO_DRIFT - Discord alert skipped."
                    }
                }
            }
        }

        stage('Security Gate') {
            steps {
                script {

                    def reportStatus = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('status','UNKNOWN'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskLevel = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_level','LOW'))"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskScore = bat(
                        script: '''
                            venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d.get('risk_score',0))"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "========================================"
                    echo "           SECURITY GATE"
                    echo "========================================"
                    echo "Security Gate: ${reportStatus}"
                    echo "Risk Level: ${riskLevel}"
                    echo "Risk Score: ${riskScore}"
                    echo "========================================"

                    if (reportStatus == 'DRIFT_DETECTED') {

                        error(
                            "SECURITY GATE BLOCKED BUILD - ${riskLevel} risk detected (Score: ${riskScore})"
                        )

                    } else {

                        echo "Security Gate PASSED - No drift detected."
                    }
                }
            }
        }
    }

    post {

        always {
            archiveArtifacts(
                artifacts: 'reports/drift_report.json',
                allowEmptyArchive: true
            )

            bat '''
                if exist discord_payload.json del /f /q discord_payload.json
            '''
        }

        success {
            echo "========================================"
            echo " DriftGuard: BUILD SUCCESS"
            echo " No infrastructure drift detected."
            echo "========================================"
        }

        failure {
            echo "========================================"
            echo " DriftGuard: BUILD BLOCKED"
            echo " Infrastructure drift detected."
            echo " Check Jenkins + Discord alert."
            echo "========================================"
        }
    }
}