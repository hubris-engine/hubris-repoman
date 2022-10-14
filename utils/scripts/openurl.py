from argparse import ArgumentParser
import webbrowser as web

parser = ArgumentParser(description="Opens a URL in a webbrowser")
parser.add_argument("url", type=str, help="The URL to open")

args = parser.parse_args()
url : str = args.url

result = web.open(url)
if not result:
    exit(1)
else:
    exit(0)