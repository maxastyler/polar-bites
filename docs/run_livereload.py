from platform import system

from livereload import Server, shell

if __name__ == "__main__":
    s = system()
    make_command = ""
    if s == "Linux":
        make_command = "make html"
    elif s == "Windows":
        make_command = "make.bat html"
    server = Server()
    server.watch("*.rst", shell(make_command), delay=1)
    server.watch("*.md", shell(make_command), delay=1)
    server.watch("*.py", shell(make_command), delay=1)
    server.watch("../polar_bites/**/*.py)", shell(make_command), delay=1)
    server.watch("_static/*", shell(make_command), delay=1)
    server.watch("_templates/*", shell(make_command), delay=1)
    server.serve(root="_build/html")
