pipeline {
    agent {
        docker {
            image 'python:3.6.7'
        }
    }
    stages {
        stage('Setup') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'pip install -r requirements.txt --user'
                }
            }
        }
        stage('Python tests') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python -m pytest tests'
                }
            }
        }
        stage('Shell tests') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'integration-tests/test_cleaning.sh'
                }
            }
        }
    }
}
