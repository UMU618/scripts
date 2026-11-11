$gitlabHost = "192.168.31.200"
$out = "C:\GitLab-Runner\certs\$gitlabHost.crt"

New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
$tcp = New-Object Net.Sockets.TcpClient($gitlabHost, 443)
$cb  = [Net.Security.RemoteCertificateValidationCallback]{ param($s,$c,$ch,$e) $true }
$ssl = New-Object Net.Security.SslStream($tcp.GetStream(), $false, $cb)
$ssl.AuthenticateAsClient($gitlabHost)
$cert = [Security.Cryptography.X509Certificates.X509Certificate2]$ssl.RemoteCertificate
$cert | Format-List Subject, Issuer, NotBefore, NotAfter
$b64 = [Convert]::ToBase64String($cert.RawData)
$b64_lines = for ($i = 0; $i -lt $b64.Length; $i += 64) {
    $len = [Math]::Min(64, $b64.Length - $i)
    $b64.Substring($i, $len)
}
$b64 = $b64_lines -join "`n"
[IO.File]::WriteAllText($out, "-----BEGIN CERTIFICATE-----`n$b64`n-----END CERTIFICATE-----`n", [Text.Encoding]::ASCII)
$ssl.Dispose(); $tcp.Dispose()
