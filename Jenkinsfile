pipeline {

    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-driftguard')
        AWS_SECRET_ACCESS_KEY = credentials('aws-driftguard')
        AWS_DEFAULT_REGION    = 'ap-south-1'
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
                bat 'venv\\Scripts\\python -c "import boto3; print(boto3.client(''sts'').get_caller_identity()[''Arn''])"'
            }
        }

        stage('Drift Detection') {
            steps {
                bat 'venv\\Scripts\\python detector\\drift_detector.py'
            }
        }

        stage('Risk Analysis') {
            steps {
                bat 'venv\\Scripts\\python detector\\risk_engine.py'
            }
        }
    }

    post {
        always {
            echo 'DriftGuard pipeline execution completed.'
        }
    }
}