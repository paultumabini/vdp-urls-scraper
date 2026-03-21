import ftplib

ftp = ftplib.FTP()
host = "aim-control.com"
port = 21
ftp.connect(host, port)
print(ftp.getwelcome())
try:
    print("Logged in...")
    ftp.login('gen_ftp', 'G3Nftp!')
except:
    "failed to login"

    # send or create csv in ftp server
import io
from ftplib import FTP

csvfile = io.StringIO()
import csv

fieldnames = ['VIN', 'VDP URLS']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

writer.writeheader()
writer.writerow(
    {
        'VIN': '3C6UR5TL2KG517011',
        'VDP URLS': 'https://www.macdonaldbuickgmc.com/inventory/certified-used-2019-ram-2500-limited-certified-leather-seats-610-bw-4x4-crew-cab-3c6ur5tl2kg517011/',
    }
)
writer.writerow(
    {
        'VIN': '1GTUUCED3NZ581385',
        'VDP URLS': 'https://www.macdonaldbuickgmc.com/inventory/new-2022-gmc-sierra-1500-elevation-452-bw-4x4-crew-cab-1gtuuced3nz581385/',
    }
)
writer.writerow(
    {
        'VIN': '3C6UR5TL2KG517011',
        'VDP URLS': 'https://www.macdonaldbuickgmc.com/inventory/new-2022-gmc-sierra-1500-elevation-452-bw-4x4-crew-cab-1gtuuced3nz597201/',
    }
)

ftp = FTP('aim-admin.com')
ftp.login('gen_ftp', 'G3Nftp!')
# flo.seek(0)
# ftp.set_pasv(False)
ftp.storbinary('STOR TEST_VDP_URLS.csv', io.BytesIO(csvfile.getvalue().encode()))
print("SENT...")
