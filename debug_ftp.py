import requests

url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
resp = requests.get(url, timeout=20)
lines = resp.text.strip().split("\n")
print("Total lines:", len(lines))
print("Header:", lines[0])
print("First 5 data lines:")
for l in lines[1:6]:
    print(" ", l)
print("Last line:", lines[-1])
