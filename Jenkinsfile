pipeline {
    agent any

    environment {
        IMAGE_NAME = 'selenium-test-runner'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Run Tests in Container') {
            steps {
                sh '''
                    docker run --rm $IMAGE_NAME
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Selenium tests passed inside Docker container!'
        }
        failure {
            echo '❌ Selenium tests failed inside Docker container!'
        }
    }
}

