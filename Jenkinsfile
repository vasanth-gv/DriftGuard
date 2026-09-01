pipeline {

    agent any

    environment {

        AWS_DEFAULT_REGION = 'ap-south-1'

        PYTHONIOENCODING = 'utf-8'

        // IMPORTANT:
        // Change this to the Gmail address where you want
        // to receive the DriftGuard alert.
        EMAIL_TO = 'guruvasanth097@gmail.com'

        EMAIL_FROM = 'guru08092004ff@gmail.com'
    }

    stages {

        // =====================================================
        // 1. CHECKOUT
        // =====================================================

        stage('Checkout') {

            steps {

                checkout scm

            }
        }


        // =====================================================
        // 2. PYTHON SETUP
        // =====================================================

        stage('Python Setup') {

            steps {

                bat '''
                python -m venv venv
                '''

                bat '''
                venv\\Scripts\\python -m pip install -r requirements.txt
                '''

            }
        }


        // =====================================================
        // 3. AWS AUTHENTICATION
        // =====================================================

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


        // =====================================================
        // 4. DRIFT DETECTION
        // =====================================================

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


        // =====================================================
        // 5. RISK ANALYSIS
        // =====================================================

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


        // =====================================================
        // 6. EMAIL ALERT
        // =====================================================

        stage('Email Alert') {

            steps {

                script {

                    // ---------------------------------------------
                    // Read drift_report.json using Python
                    // No Pipeline Utility Steps plugin required.
                    // ---------------------------------------------

                    def result = bat(

                        script: '''
                        @echo off

                        venv\\Scripts\\python -c "import json; r=json.load(open('reports/drift_report.json')); print(r['status']); print(r['risk']['level']); print(r['risk']['score'])"

                        ''',

                        returnStdout: true

                    ).trim()


                    // ---------------------------------------------
                    // Remove empty lines from Windows BAT output
                    // ---------------------------------------------

                    def lines = result
                        .readLines()
                        .findAll { it != null && it.trim() != '' }


                    // ---------------------------------------------
                    // Last 3 lines contain:
                    //
                    // STATUS
                    // RISK LEVEL
                    // RISK SCORE
                    // ---------------------------------------------

                    if (lines.size() < 3) {

                        error(
                            "Unable to parse drift_report.json output. Output was: ${result}"
                        )

                    }


                    def status = lines[-3].trim()

                    def riskLevel = lines[-2].trim()

                    def riskScore = lines[-1].trim()


                    // ---------------------------------------------
                    // Display results
                    // ---------------------------------------------

                    echo "========================================="

                    echo "Drift Status: ${status}"

                    echo "Risk Level: ${riskLevel}"

                    echo "Risk Score: ${riskScore}"

                    echo "========================================="


                    // =================================================
                    // DRIFT DETECTED
                    // =================================================

                    if (status == 'DRIFT_DETECTED') {

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
                                infrastructure change in AWS.
                                </p>

                                <p>
                                <b>AWS Region:</b>
                                ${env.AWS_DEFAULT_REGION}
                                </p>

                                <p>
                                <b>Jenkins Job:</b>
                                ${env.JOB_NAME}
                                </p>

                                <p>
                                <b>Jenkins Build:</b>
                                #${env.BUILD_NUMBER}
                                </p>

                                <p>
                                <b>Build URL:</b>
                                ${env.BUILD_URL}
                                </p>

                                <hr>

                                <h3>Security Action</h3>

                                <p>
                                The DriftGuard Security Gate has blocked
                                the pipeline because unauthorized
                                infrastructure drift was detected.
                                </p>

                                <hr>

                                <p>
                                <b>DriftGuard CI/CD Security Pipeline</b>
                                </p>

                                </body>

                                </html>

                                """

                            )


                            echo "========================================="

                            echo "DRIFT DETECTED"

                            echo "Email alert submitted successfully."

                            echo "Recipient: ${env.EMAIL_TO}"

                            echo "========================================="

                        }


                        catch (Exception e) {

                            echo "========================================="

                            echo "EMAIL ALERT FAILED"

                            echo "Error: ${e.getMessage()}"

                            echo "========================================="

                            echo "Security Gate will still evaluate the drift."

                        }

                    }


                    // =================================================
                    // NO DRIFT
                    // =================================================

                    else {

                        echo "========================================="

                        echo "NO DRIFT DETECTED"

                        echo "Email alert skipped."

                        echo "========================================="

                    }

                }

            }

        }


        // =====================================================
        // 7. SECURITY GATE
        // =====================================================

        stage('Security Gate') {

            steps {

                bat '''

                venv\\Scripts\\python -c "import json,sys; r=json.load(open('reports/drift_report.json')); print('Security Gate: '+r['status']); print('Risk Level: '+r['risk']['level']); print('Risk Score: '+str(r['risk']['score'])); sys.exit(1 if r['status']=='DRIFT_DETECTED' else 0)"

                '''

            }
        }

    }


    // =========================================================
    // POST ACTIONS
    // =========================================================

    post {

        always {

            archiveArtifacts(

                artifacts: 'reports/drift_report.json',

                allowEmptyArchive: true

            )


            echo "========================================="

            echo "DriftGuard pipeline execution completed."

            echo "========================================="

        }

    }

}