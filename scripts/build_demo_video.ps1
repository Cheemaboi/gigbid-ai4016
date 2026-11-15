param(
  [string]$FrameDir = "artifacts/demo-frames",
  [string]$OutputDir = "artifacts/demo-video"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$frames = Join-Path $root $FrameDir
$output = Join-Path $root $OutputDir
New-Item -ItemType Directory -Force -Path $output | Out-Null

$narration = @'
Welcome to GigBid, a human-approved freelance proposal copilot. This deployed React and FastAPI application helps a freelancer decide which opportunities are worth pursuing while keeping every external action under human control.

The inbox ranks three saved opportunities. For each job, the reviewer sees a budget, skills, suggested bid, Connects cost, fit score, and risk score. The first job is an inventory forecasting API with Python and FastAPI requirements. I start a safe analysis; nothing is submitted to any marketplace.

The workflow is an executable LangGraph. Scout loads the job, then analyst, fit, and risk checks fan out in parallel. The graph joins at a decision, produces a price, writes a proposal, verifies claims, and runs compliance. The trail ends at an explicit human approval interruption. The evidence matrix shows the portfolio items supporting the recommendation, and the price rationale remains visible for review.

The proposal studio is the approval boundary. It presents an editable draft with every claim labelled supported, partly supported, or unsupported. Approval requires the reviewer account and produces only an idempotent dry-run preview. It never sends a proposal or spends Connects automatically.

Now I select the unsafe job. Its description asks for free sample work, off-platform Telegram contact, and instructions to ignore the platform rules. GigBid treats that text as untrusted data, flags the risk, and skips drafting. This shows the safety policy operating before a proposal exists.

The project also exposes a public Streamable HTTP Portfolio MCP server. Its tools search portfolio evidence, retrieve case studies, and list skills through a verified MCP initialization. The research corpus includes an attributed, redacted sample of public job posts, while portfolio data and evaluation labels are clearly identified as synthetic. The included evaluation is a reproducible smoke test, not a claim about real marketplace performance. Thank you for reviewing GigBid.
'@

$narrationPath = Join-Path $output "narration.wav"
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice("Microsoft Zira Desktop")
$voice.Rate = -1
$voice.SetOutputToWaveFile($narrationPath)
$voice.Speak($narration)
$voice.Dispose()

$font = "C\:/Windows/Fonts/arialbd.ttf"
$clips = @(
  @{ Frame = "01-inbox.png"; Seconds = 35; Caption = "Live deployed dashboard - ranked opportunities and decision inputs" },
  @{ Frame = "02-analysis.png"; Seconds = 45; Caption = "LangGraph decision trail - evidence, risk, pricing and human interrupt" },
  @{ Frame = "03-approval.png"; Seconds = 50; Caption = "Human approval gate - editable proposal with grounded claim checks" },
  @{ Frame = "04-safety.png"; Seconds = 50; Caption = "Safety case - off-platform and free-work request is skipped" }
)

$concat = Join-Path $output "clips.txt"
$concatLines = @()
for ($index = 0; $index -lt $clips.Count; $index++) {
  $clip = $clips[$index]
  $input = Join-Path $frames $clip.Frame
  $clipPath = Join-Path $output ("clip-{0}.mp4" -f $index)
  $caption = $clip.Caption.Replace("'", "\\'")
  $filter = "scale=1440:900,drawbox=x=0:y=820:w=1440:h=80:color=0x0F2850@0.92:t=fill,drawtext=fontfile='$font':text='$caption':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=846"
  & ffmpeg -hide_banner -loglevel error -y -loop 1 -i $input -t $clip.Seconds -vf $filter -r 30 -pix_fmt yuv420p $clipPath
  $concatLines += "file '$($clipPath.Replace('\','/'))'"
}
Set-Content -LiteralPath $concat -Value $concatLines -Encoding ascii

$silentVideo = Join-Path $output "gigbid-demo-visuals.mp4"
& ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i $concat -c copy $silentVideo

$final = Join-Path $output "GigBid_3_Minute_Demo.mp4"
& ffmpeg -hide_banner -loglevel error -y -i $silentVideo -i $narrationPath -filter_complex "[1:a]apad=pad_dur=180[a]" -map 0:v -map "[a]" -t 180 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -movflags +faststart $final

& ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 $final
Write-Output $final
