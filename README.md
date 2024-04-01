# Recognizer
An ML application server written in Python that processes the request and sends response in MusicXML. Uses Flask to build http server.

## Commands
- `make start`: Starts the development server. Make sure you activate the virtual env first to run this command.
- `make output`: Starts the development server with save-on-process option checked. This will save the generated files into the `/out` folder.
- `make clean`: Removed `/out` and `/temp` folders from the working space.

## Useful Links
- [MusicXML Specification](https://www.w3.org/2021/06/musicxml40/tutorial/introduction/)