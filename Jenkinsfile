#!/usr/bin/env groovy

node('robxtask-jenkins-slave') {

    // -----------------------------------------------
    // --------------- Staging Branch ----------------
    // -----------------------------------------------
    if (env.BRANCH_NAME == 'staging') {

        stage('Clone and Update') {
            git(url: 'https://github.com/ROBxTASK/codegen-service.git', branch: env.BRANCH_NAME)
        }

        stage('Build Docker') {
            sh 'docker build ./server -t robxtask/codegen-service:staging'
        }

        stage('Push Docker - staging') {
            withCredentials([usernamePassword(credentialsId: 'docker-login-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                sh 'docker login --username $USER --password $PASS'
                sh 'docker push robxtask/codegen-service:staging'
            }
        }

        stage('Deploy') {
            sh 'ssh staging "cd /srv/docker-setup/staging/ && ./run-staging.sh restart-single codegen-service"'
        }
    }
}