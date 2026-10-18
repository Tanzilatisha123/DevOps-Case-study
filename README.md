# Student Task Manager – Flask + Docker + Kubernetes + Jenkins

## 1. Run locally
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python app.py            # http://localhost:5000
    pytest -q

## 2. Docker
    docker build -t student-task-manager .
    docker run -p 5000:5000 student-task-manager

## 3. Git
    git init && git add . && git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/<you>/student-task-manager.git
    git push -u origin main

## 4. Kubernetes (minikube / Docker Desktop)
    sed 's|DOCKERHUB_USER/student-task-manager:IMAGE_TAG|<you>/student-task-manager:latest|' k8s/deployment.yaml | kubectl apply -f -
    kubectl apply -f k8s/service.yaml
    kubectl get pods,svc
    minikube service student-task-manager-svc --url     # or http://localhost:30007 on Docker Desktop

## 5. Jenkins setup
1. Run Jenkins on a machine that has docker, kubectl, python3 (add the jenkins user to the docker group).
2. Plugins: Git, GitHub, Pipeline, Credentials Binding.
3. Credentials (Manage Jenkins > Credentials):
   - `dockerhub-creds` – Username/Password (use a Docker Hub access token)
   - `kubeconfig` – Secret file (your ~/.kube/config)
4. New Item > Pipeline > "Pipeline script from SCM" > Git > repo URL, branch `main`, script path `Jenkinsfile`.
   Tick "GitHub hook trigger for GITScm polling".
5. GitHub repo > Settings > Webhooks > Payload URL `http://<jenkins-host>:8080/github-webhook/`, content type application/json, event: push.
   (Jenkins on localhost? Expose it with `ngrok http 8080` and use that URL.)

## 6. Demo
Edit a template (e.g. change the heading in dashboard.html), `git commit && git push`.
Jenkins triggers automatically -> builds image -> pushes -> `kubectl apply` -> refresh the browser to see the change.
