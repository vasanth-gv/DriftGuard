pipeline {

    agent any

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