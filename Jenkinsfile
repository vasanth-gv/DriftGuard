pipeline {
    agent any

    triggers {
        cron('H/5 * * * *')
    }

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        PYTHONIOENCODING = 'utf-8'

        EMAIL_TO = 'guru08092004ff@gmail.com'
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
                        @venv\\Scripts\\python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Arn'])"
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
                        @venv\\Scripts\\python detector\\drift_detector.py
                    '''
                }
            }
        }

        stage('Risk Analysis') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskLevel = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d['risk']['level'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def riskScore = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d['risk']['score'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def reason = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; d=json.load(open('reports/drift_report.json')); print(d['risk']['reason'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo '''
========================================
      DRIFTGUARD RISK ANALYSIS
========================================
'''

                    echo "Status      : ${status}"
                    echo "Risk Level  : ${riskLevel}"
                    echo "Risk Score  : ${riskScore}"
                    echo "Reason      : ${reason}"

                    echo '========================================'
                }
            }
        }

        stage('Email Alert') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    if (status == 'DRIFT_DETECTED') {

                        def level = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['level'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def score = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['score'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def reason = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['reason'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        try {

                            emailext(
                                to: "${env.EMAIL_TO}",
                                from: "${env.EMAIL_FROM}",
                                replyTo: "${env.EMAIL_FROM}",
                                subject: "DriftGuard ALERT - ${level} Risk - Build #${env.BUILD_NUMBER}",
                                mimeType: 'text/html',
                                body: """
                                    <h2>🚨 DriftGuard Security Alert</h2>

                                    <p><b>Status:</b> ${status}</p>
                                    <p><b>Risk Level:</b> ${level}</p>
                                    <p><b>Risk Score:</b> ${score}</p>
                                    <p><b>Reason:</b> ${reason}</p>

                                    <hr>

                                    <p><b>Resource:</b> driftguard-web-sg</p>
                                    <p><b>Region:</b> ap-south-1</p>
                                    <p><b>Jenkins Build:</b> #${env.BUILD_NUMBER}</p>

                                    <p>
                                        <b>Action:</b>
                                        Security Gate will block the build.
                                    </p>
                                """
                            )

                            echo 'Email alert submitted.'

                        } catch (Exception e) {
                            echo "Email alert failed: ${e.message}"
                        }

                    } else {

                        echo 'NO_DRIFT - Email skipped.'

                    }
                }
            }
        }

        stage('Discord Alert') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    if (status == 'DRIFT_DETECTED') {

                        def level = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['level'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def score = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['score'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def reason = bat(
                            script: '''
                                @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['reason'])"
                            ''',
                            returnStdout: true
                        ).trim()

                        def message = """🚨 **DriftGuard Security Alert**

🔴 **Status:** ${status}
⚠️ **Risk Level:** ${level}
📊 **Risk Score:** ${score}

🖥️ **Resource:** driftguard-web-sg
🌍 **Region:** ap-south-1

🔓 **Reason:** ${reason}

🚫 **Security Gate:** BUILD BLOCKED
🔧 **Jenkins Build:** #${env.BUILD_NUMBER}
"""

                        withCredentials([
                            string(
                                credentialsId: 'discord-webhook',
                                variable: 'DISCORD_WEBHOOK'
                            )
                        ]) {

                            def payload = groovy.json.JsonOutput.toJson([
                                content: message
                            ])

                            writeFile(
                                file: 'discord.json',
                                text: payload
                            )

                            bat '''
                                @curl -s -X POST ^
                                -H "Content-Type: application/json" ^
                                --data-binary "@discord.json" ^
                                "%DISCORD_WEBHOOK%"
                            '''
                        }

                        echo 'Discord alert sent successfully.'

                    } else {

                        echo 'NO_DRIFT - Discord skipped.'

                    }
                }
            }
        }

        stage('Security Gate') {
            steps {
                script {

                    def status = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['status'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def level = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['level'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    def score = bat(
                        script: '''
                            @venv\\Scripts\\python -c "import json; print(json.load(open('reports/drift_report.json'))['risk']['score'])"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo '''
========================================
         SECURITY GATE
========================================
'''

                    echo "Status      : ${status}"
                    echo "Risk Level  : ${level}"
                    echo "Risk Score  : ${score}"

                    echo '========================================'

                    if (status == 'DRIFT_DETECTED') {

                        error(
                            "SECURITY GATE BLOCKED BUILD - ${level} Risk (${score})"
                        )

                    } else {

                        echo 'Security Gate PASSED'

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
                @if exist discord.json del /f /q discord.json
            '''

            echo 'DriftGuard pipeline execution completed.'
        }

        success {
            echo 'BUILD SUCCESS'
        }

        failure {
            echo 'BUILD BLOCKED DUE TO DRIFT'
        }
    }
}