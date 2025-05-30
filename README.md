First step is to add open webui API key. All LLM endpoints hit the open webui apis.
Second step is to run bash manage.sh --start from the command lin

Managmenet services:
From the top level director run the following bash command:

manage.sh --start     # Start and build services
manage.sh --stop      # Stop and clean everything
manage.sh --status    # Show container status
manage.sh --logs      # View real-time logs
