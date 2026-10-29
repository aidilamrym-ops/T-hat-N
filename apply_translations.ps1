# PowerShell script to translate Indonesian UI/ documentation strings to English
# Target files: *.md, *.txt, *.lean, *.py
# Only replace plain words, not code identifiers.

$replacements = @(
    @{'old'='\bdan\b';'new'='and'},
    @{'old'='\batau\b';'new'='or'},
    @{'old'='\byang\b';'new'='which'},
    @{'old'='\buntuk\b';'new'='for'},
    @{'old'='\bdi\b';'new'='in'},
    @{'old'='\bpada\b';'new'='on'},
    @{'old'='\btidak\b';'new'='no'},
    @{'old'='\bberkas\b';'new'='file'},
    @{'old'='\bbatas\b';'new'='limit'},
    @{'old'='\bcatatan\b';'new'='note'},
    @{'old'='\bketerangan\b';'new'='description'},
    @{'old'='\bbagian\b';'new'='section'},
    @{'old'='\bstatus\b';'new'='status'},
    @{'old'='\blangkah\b';'new'='step'},
    @{'old'='\btindakan\b';'new'='action'},
    @{'old'='\bhasil\b';'new'='result'},
    @{'old'='\blaporan\b';'new'='report'},
    @{'old'='\bpengujian\b';'new'='testing'},
    @{'old'='\bpengaturan\b';'new'='configuration'},
    @{'old'='\bpengembang\b';'new'='developer'},
    @{'old'='\bpertanyaan\b';'new'='question'},
    @{'old'='\bjawaban\b';'new'='answer'},
    @{'old'='\bsumber\b';'new'='source'},
    @{'old'='\bpath\b';'new'='path'},
    @{'old'='\bdirektori\b';'new'='directory'},
    @{'old'='\bsudah\b';'new'='already'},
    @{'old'='\btidak ada\b';'new'='none'},
    @{'old'='\bdi dalam\b';'new'='in the'},
    @{'old'='\bdengan\b';'new'='with'},
    @{'old'='\bmemverifikasi\b';'new'='verifying'},
    @{'old'='\bdibuat\b';'new'='created'},
    @{'old'='\bditerbitkan\b';'new'='published'},
    @{'old'='\bditandai\b';'new'='marked'}
)

# Process markdown, txt, py files (replace anywhere)
Get-ChildItem -Recurse -Include *.md,*.txt,*.py | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    foreach ($rep in $replacements) {
        $content = [regex]::Replace($content, $rep.old, $rep.new)
    }
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}

# Process Lean files: only replace in comment lines (starting with --)
Get-ChildItem -Recurse -Include *.lean | ForEach-Object {
    $lines = Get-Content $_.FullName
    $changed = $false
    for ($i=0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match '^\s*--') {
            foreach ($rep in $replacements) {
                $new = [regex]::Replace($line, $rep.old, $rep.new)
                if ($new -ne $line) { $line = $new; $changed = $true }
            }
            $lines[$i] = $line
        }
    }
    if ($changed) { Set-Content -Path $_.FullName -Value $lines -Encoding UTF8 }
}

Write-Host "Translation replacements applied."
