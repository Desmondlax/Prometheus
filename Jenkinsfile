
pipeline {
    agent { 
        node {
            label 'docker-agent-fastapi'
            }
      }
	triggers {
        pollSCM 'H * * * *'
	  }
    environment {
        PATH="/home/jenkins/.local/bin:$PATH"
    }
    stages {
        stage('Clone') {
            steps {
                git branch: "main", url: "https://github.com/Desmondlax/Prometheus.git" 
            }
        }
        stage('Building & Testing in parallel'){
            parallel{
                stage('Build') {
                    steps {
                            timeout(time: 10, unit: 'MINUTES'){
                                echo "Starting the build..."
                                sh '''
                                pip install --no-cache-dir --upgrade -r /home/jenkins/workspace/prometheus_test/requirements.txt --break-system-packages
                                uvicorn main:app --reload --host 127.0.0.1 --port 80 > /home/jenkins/workspace/prometheus_test/api_output.log 2>&1
                                ''' 
                            }
                            
                    }
                }
                stage('Test') {
                    steps {
                        sh '''
                        sleep 300
                        '''
                        echo "Testing.."
                        script {
                            def url = 'http://127.0.0.1:80/'
                            def maxRetries = 5
                            def retryDelay = 5

                            for (int i=0; i < maxRetries; i++){
                                try {
                                    def status = sh(
                                        script: "curl --write-out '%{http_code}' -o /dev/null ${url}",
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
                            def fastapi_pid = sh( script: "head -n 4 /home/jenkins/workspace/prometheus_test/api_output.log | grep -o '[[:digit:]]*' | tail -1", returnStdout: true).trim()
                            echo "${fastapi_pid}"
                            sh "kill -INT ${fastapi_pid}"
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