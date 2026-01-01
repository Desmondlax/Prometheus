pipeline {
    agent { 
        node {
            label 'docker-agent-fastapi'
            }
      }
	triggers {
        pollSCM 'H * * * *'
	  }
    stages {
        stage('Clone') {
            steps {
                git branch: "main", url: "https://github.com/Desmondlax/Prometheus.git" 
            }
        }
        stage('Build') {
            steps {
                echo "Starting the build..."
                sh '''
                echo "$PWD"
                python3 -m venv /path/to/venv
                . /path/to/venv/bin/activate
                pip install --no-cache-dir --upgrade -r /home/jenkins/workspace/prometheus_test/requirements.txt
				uvicorn main:app --reload --host 127.0.0.1 --port 80
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Testing.."
                script {
                    def url = 'http://127.0.0.1:80/'
                    def maxRetries = 5
                    def retryDelay = 5
                    
                    for (int i=0; i < maxRetries; i++){
                        try {
                            def status = sh(
                                script: "curl -sLI -w '%{http_code}' ${url} -o /dev/null",
                                returnStdout: true
                            ).trim()

                            echo "Attempt ${i + 1}: Received status code ${status}"

                            if (status == "200" || status == "201") {
                                echo "Connectivity successful!"
                                break // Exit the loop on success
                            }
                        } catch (Exception e) {
                            echo "Attempt ${i + 1}: Connection failed. Retrying in ${retryDelay} seconds..."
                        }

                        if (i < maxRetries - 1) {
                            sleep retryDelay
                        } else {
                            error("Max retries reached. Failed to connect to ${url}") // Fail the pipeline
                        }
                    }
                    
                }
                
            }
        }
        stage('Deliver') {
            steps {
                echo 'Deliver....'
                sh '''
                echo "doing delivery stuff.."
                '''
            }
        }
    }
}