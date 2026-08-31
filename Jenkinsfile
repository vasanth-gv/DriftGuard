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
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/drift_report.json',
                             allowEmptyArchive: true

            echo 'DriftGuard pipeline execution completed.'
        }
    }
}