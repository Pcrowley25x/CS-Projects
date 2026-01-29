using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Timer = System.Windows.Forms.Timer;

namespace QuizGameClientGUI
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LoginForm());
        }
    }

    public class LoginForm : Form
    {
        private TextBox nameTextBox = null!;
        private TextBox ipTextBox = null!;
        private Button connectButton = null!;

        public LoginForm()
        {
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            this.Text = "Quiz Game - Connect";
            this.Size = new Size(500, 400);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(30, 30, 46);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;

            var titleLabel = new Label
            {
                Text = "🎮 QUIZ SHOWDOWN",
                Font = new Font("Segoe UI", 28, FontStyle.Bold),
                ForeColor = Color.FromArgb(137, 180, 250),
                AutoSize = false,
                Size = new Size(460, 60),
                Location = new Point(20, 30),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var nameLabel = new Label
            {
                Text = "Player Name:",
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                ForeColor = Color.FromArgb(205, 214, 244),
                Location = new Point(50, 120),
                AutoSize = true
            };

            nameTextBox = new TextBox
            {
                Font = new Font("Segoe UI", 14),
                Location = new Point(50, 150),
                Size = new Size(400, 35),
                BackColor = Color.FromArgb(49, 50, 68),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };

            var ipLabel = new Label
            {
                Text = "Server IP (leave blank for localhost):",
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                ForeColor = Color.FromArgb(205, 214, 244),
                Location = new Point(50, 200),
                AutoSize = true
            };

            ipTextBox = new TextBox
            {
                Font = new Font("Segoe UI", 14),
                Location = new Point(50, 230),
                Size = new Size(400, 35),
                BackColor = Color.FromArgb(49, 50, 68),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Text = "127.0.0.1"
            };

            connectButton = new Button
            {
                Text = "CONNECT",
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                Location = new Point(150, 300),
                Size = new Size(200, 50),
                BackColor = Color.FromArgb(137, 180, 250),
                ForeColor = Color.FromArgb(30, 30, 46),
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand
            };
            connectButton.FlatAppearance.BorderSize = 0;
            connectButton.Click += ConnectButton_Click;

            this.Controls.AddRange(new Control[] { titleLabel, nameLabel, nameTextBox, ipLabel, ipTextBox, connectButton });
        }

        private void ConnectButton_Click(object? sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(nameTextBox.Text))
            {
                MessageBox.Show("Please enter your name!", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            connectButton.Enabled = false;
            connectButton.Text = "Connecting...";

            try
            {
                var serverIp = string.IsNullOrWhiteSpace(ipTextBox.Text) ? "127.0.0.1" : ipTextBox.Text;
                var client = new TcpClient(serverIp, 5001);
                var gameForm = new GameForm(client, nameTextBox.Text);

                this.Hide();
                gameForm.FormClosed += (s, args) => this.Close();
                gameForm.Show();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Connection failed: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                connectButton.Enabled = true;
                connectButton.Text = "CONNECT";
            }
        }
    }

    public class GameForm : Form
    {
        private TcpClient client;
        private NetworkStream stream;
        private string playerName;

        private Label statusLabel = null!;
        private Label questionLabel = null!;
        private Label timerLabel = null!;
        private Button[] answerButtons = null!;
        private Panel scorePanel = null!;
        private Label scoreLabel = null!;

        private int timeRemaining;
        private Timer countdownTimer = null!;
        private bool answerSubmitted;

        public GameForm(TcpClient client, string playerName)
        {
            this.client = client;
            this.playerName = playerName;
            this.stream = client.GetStream();

            InitializeComponents();

            // Make sure the form is fully loaded before starting to receive messages
            this.Load += (s, e) =>
            {
                SendPlayerName();
                Task.Run(() => ReceiveMessages());
            };
        }

        private void InitializeComponents()
        {
            this.Text = $"Quiz Game - {playerName}";
            this.Size = new Size(900, 700);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(30, 30, 46);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;

            statusLabel = new Label
            {
                Text = "Waiting for game to start...",
                Font = new Font("Segoe UI", 18, FontStyle.Bold),
                ForeColor = Color.FromArgb(166, 227, 161),
                Location = new Point(50, 30),
                Size = new Size(800, 40),
                TextAlign = ContentAlignment.MiddleCenter
            };

            questionLabel = new Label
            {
                Text = "",
                Font = new Font("Segoe UI", 20, FontStyle.Bold),
                ForeColor = Color.FromArgb(205, 214, 244),
                Location = new Point(50, 100),
                Size = new Size(800, 100),
                TextAlign = ContentAlignment.MiddleCenter
            };

            timerLabel = new Label
            {
                Text = "",
                Font = new Font("Segoe UI", 48, FontStyle.Bold),
                ForeColor = Color.FromArgb(243, 139, 168),
                Location = new Point(350, 220),
                Size = new Size(200, 80),
                TextAlign = ContentAlignment.MiddleCenter
            };

            answerButtons = new Button[4];
            var colors = new[]
            {
                Color.FromArgb(137, 180, 250),
                Color.FromArgb(166, 227, 161),
                Color.FromArgb(250, 179, 135),
                Color.FromArgb(243, 139, 168)
            };

            for (int i = 0; i < 4; i++)
            {
                int row = i / 2;
                int col = i % 2;

                answerButtons[i] = new Button
                {
                    Text = "",
                    Font = new Font("Segoe UI", 14, FontStyle.Bold),
                    Location = new Point(50 + col * 420, 330 + row * 100),
                    Size = new Size(380, 80),
                    BackColor = colors[i],
                    ForeColor = Color.FromArgb(30, 30, 46),
                    FlatStyle = FlatStyle.Flat,
                    Cursor = Cursors.Hand,
                    Tag = i,
                    Visible = false
                };
                answerButtons[i].FlatAppearance.BorderSize = 0;
                answerButtons[i].Click += AnswerButton_Click;

                this.Controls.Add(answerButtons[i]);
            }

            scorePanel = new Panel
            {
                Location = new Point(50, 550),
                Size = new Size(800, 100),
                BackColor = Color.FromArgb(49, 50, 68),
                Visible = false
            };

            scoreLabel = new Label
            {
                Text = "",
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                ForeColor = Color.FromArgb(205, 214, 244),
                Location = new Point(20, 10),
                Size = new Size(760, 80),
                TextAlign = ContentAlignment.TopLeft
            };

            scorePanel.Controls.Add(scoreLabel);

            countdownTimer = new Timer();
            countdownTimer.Interval = 1000;
            countdownTimer.Tick += CountdownTimer_Tick;

            this.Controls.AddRange(new Control[] { statusLabel, questionLabel, timerLabel, scorePanel });
        }

        private void SendPlayerName()
        {
            byte[] data = Encoding.UTF8.GetBytes(playerName);
            stream.Write(data, 0, data.Length);
        }

        private async Task ReceiveMessages()
        {
            byte[] buffer = new byte[4096];

            try
            {
                while (true)
                {
                    int bytes = await stream.ReadAsync(buffer, 0, buffer.Length);
                    if (bytes == 0) break;

                    string msg = Encoding.UTF8.GetString(buffer, 0, bytes);

                    System.Diagnostics.Debug.WriteLine($"Received: {msg}");

                    if (this.IsHandleCreated && !this.IsDisposed)
                    {
                        this.BeginInvoke((Action)(() => ProcessMessage(msg)));
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Receive error: {ex.Message}");
                if (this.IsHandleCreated && !this.IsDisposed)
                {
                    this.BeginInvoke((Action)(() =>
                    {
                        MessageBox.Show($"Disconnected: {ex.Message}", "Connection Lost");
                        this.Close();
                    }));
                }
            }
        }

        private void ProcessMessage(string msg)
        {
            System.Diagnostics.Debug.WriteLine($"Processing: {msg}");

            var parts = msg.Split('|');

            if (parts.Length == 0) return;

            switch (parts[0])
            {
                case "WELCOME":
                    statusLabel.Text = $"Connected as {playerName}! Waiting for game...";
                    statusLabel.ForeColor = Color.FromArgb(166, 227, 161);
                    break;

                case "GAME_START":
                    statusLabel.Text = "🎮 GAME STARTING!";
                    statusLabel.ForeColor = Color.FromArgb(137, 180, 250);
                    questionLabel.Text = "";
                    timerLabel.Text = "";
                    scorePanel.Visible = false;
                    foreach (var btn in answerButtons)
                        btn.Visible = false;
                    break;

                case "QUESTION":
                    if (parts.Length >= 7)
                        HandleQuestion(parts);
                    break;

                case "ANSWER":
                    if (parts.Length >= 3)
                        ShowCorrectAnswer(parts);
                    break;

                case "SCORES":
                    ShowFinalScores(parts);
                    break;

                default:
                    System.Diagnostics.Debug.WriteLine($"Unknown message type: {parts[0]}");
                    break;
            }
        }

        private void HandleQuestion(string[] parts)
        {
            answerSubmitted = false;
            int questionNum = int.Parse(parts[1]);
            string questionText = parts[2];

            statusLabel.Text = $"Question {questionNum}";
            statusLabel.ForeColor = Color.FromArgb(137, 180, 250);
            questionLabel.Text = questionText;

            for (int i = 0; i < 4; i++)
            {
                answerButtons[i].Text = parts[3 + i];
                answerButtons[i].Visible = true;
                answerButtons[i].Enabled = true;
            }

            timeRemaining = 15;
            timerLabel.Text = timeRemaining.ToString();
            timerLabel.ForeColor = Color.FromArgb(166, 227, 161);
            countdownTimer.Start();
        }

        private void CountdownTimer_Tick(object? sender, EventArgs e)
        {
            timeRemaining--;
            timerLabel.Text = timeRemaining.ToString();

            if (timeRemaining <= 5)
                timerLabel.ForeColor = Color.FromArgb(243, 139, 168);

            if (timeRemaining <= 0)
            {
                countdownTimer.Stop();
                DisableAnswerButtons();
            }
        }

        private void AnswerButton_Click(object? sender, EventArgs e)
        {
            if (answerSubmitted || sender == null) return;

            var button = (Button)sender;
            int answer = (int)button.Tag;

            SendAnswer(answer);
            answerSubmitted = true;
            countdownTimer.Stop();

            DisableAnswerButtons();
            button.BackColor = Color.FromArgb(180, 190, 254);
            statusLabel.Text = "Answer submitted! ✓";
            statusLabel.ForeColor = Color.FromArgb(166, 227, 161);
        }

        private void DisableAnswerButtons()
        {
            foreach (var btn in answerButtons)
                btn.Enabled = false;
        }

        private void SendAnswer(int answer)
        {
            try
            {
                string msg = $"ANSWER|{answer}";
                byte[] data = Encoding.UTF8.GetBytes(msg);
                stream.Write(data, 0, data.Length);
            }
            catch { }
        }

        private void ShowCorrectAnswer(string[] parts)
        {
            int correctIndex = int.Parse(parts[1]);
            string correctAnswer = parts[2];

            statusLabel.Text = $"✓ Correct Answer: {correctAnswer}";
            statusLabel.ForeColor = Color.FromArgb(166, 227, 161);

            answerButtons[correctIndex].BackColor = Color.FromArgb(166, 227, 161);

            timerLabel.Text = "";
        }

        private void ShowFinalScores(string[] parts)
        {
            statusLabel.Text = "🏆 FINAL SCORES";
            statusLabel.ForeColor = Color.FromArgb(249, 226, 175);
            questionLabel.Text = "";
            timerLabel.Text = "";

            foreach (var btn in answerButtons)
                btn.Visible = false;

            var medals = new[] { "🥇", "🥈", "🥉", "  " };
            var scoreText = new StringBuilder();

            for (int i = 1; i < parts.Length; i++)
            {
                var playerScore = parts[i].Split(':');
                var medal = i <= 3 ? medals[i - 1] : medals[3];
                scoreText.AppendLine($"{medal} {i}. {playerScore[0]}: {playerScore[1]} points");
            }

            scoreLabel.Text = scoreText.ToString();
            scorePanel.Visible = true;
        }
    }
}