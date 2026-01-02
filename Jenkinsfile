
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
                            echo "Starting the build..."
                            sh '''
                            pip install --no-cache-dir --upgrade -r /home/jenkins/workspace/prometheus_test/requirements.txt --break-system-packages
                            '''
                            script{
                                def server_output = sh(script: "uvicorn main:app --reload --host 127.0.0.1 --port 80", returnStdout: true)
                            print(server_output)
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
                                        server_shutdown = true
                                        os.kill(fastapi_pid, signal.SIGINT)
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