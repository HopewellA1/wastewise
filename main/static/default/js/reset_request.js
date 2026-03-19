const EMAILJS_PUBLIC_KEY  = "CLonYWBlyChpX7bov";
  const EMAILJS_SERVICE_ID  = "dutstudent";
  const EMAILJS_TEMPLATE_ID = "template_mcl98lx";
  const APP_NAME            = "WASTEWISE";

  const ALLOWED_EXACT = [
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "icloud.com",
    "live.com"
  ];

  const ALLOWED_SUFFIXES = [
    ".ac.za",
    ".edu",
    ".ac.uk",
    ".ac.nz",
    ".edu.au"
  ];

  let correctCode    = "";
  let resendInterval = null;
  let timerInterval  = null;

  const emailInput     = document.getElementById("email-input");
  const emailError     = document.getElementById("email-error");
  const emailErrorText = document.getElementById("email-error-text");
  const sendBtn        = document.getElementById("send-btn");
  const codeInputs     = Array.from(document.querySelectorAll(".code-input"));
  const statusMsg      = document.getElementById("status-msg");
  const resendBtn      = document.getElementById("resend-btn");
  const timerBar       = document.getElementById("timer-bar");
  const card           = document.getElementById("card");

  const pillData      = ["@gmail.com", "@outlook.com", "@yahoo.com", ".ac.za", ".edu", ".ac.uk"];
  const pillContainer = document.getElementById("domain-pills");

  pillData.forEach(d => {
    const el = document.createElement("span");
    el.className = "domain-pill";
    el.textContent = d;
    pillContainer.appendChild(el);
  });

  emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });

  function isValidFormat(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function isAllowedDomain(email) {
    const domain = email.toLowerCase().split("@")[1] || "";
    if (ALLOWED_EXACT.includes(domain)) return true;
    return ALLOWED_SUFFIXES.some(s => domain.endsWith(s));
  }

  function generateCode() {
    return String(Math.floor(100000 + Math.random() * 900000));
  }

  async function sendEmail(toEmail, code) {
    return emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
      to_email: toEmail,
      code: code,
      app_name: APP_NAME
    });
  }

  function showStep(id) {
    document.querySelectorAll(".step").forEach(s => s.classList.remove("active", "fade-up"));
    const el = document.getElementById(id);
    el.classList.add("active");
    void el.offsetWidth;
    el.classList.add("fade-up");
  }

  function shakeCard() {
    card.classList.remove("shake");
    void card.offsetWidth;
    card.classList.add("shake");
    setTimeout(() => card.classList.remove("shake"), 1000);
  }

  async function handleSendCode() {
    const email = emailInput.value.trim();

    if (!isValidFormat(email)) {
      showEmailError("Please enter a valid email address.");
      shakeCard();
      return;
    }

    if (!isAllowedDomain(email)) {
      showEmailError("Only @gmail.com, .ac.za, .edu and similar domains are accepted.");
      shakeCard();
      return;
    }

    clearEmailError();
    setBtnLoading(true);
    correctCode = generateCode();

    try {
      await sendEmail(email, correctCode);
      document.getElementById("email-display").textContent = email;
      document.getElementById("success-email").textContent = email;
      emailInput.classList.add("valid");
      clearCodeInputs();
      setStatus("", "");
      showStep("step-code");
      startCountdown(120);
      startResendTimer(30);
      setTimeout(() => codeInputs[0].focus(), 150);
    } catch (err) {
      showEmailError("Could not send email. Please try again.");
      emailInput.classList.remove("valid");
      shakeCard();
    } finally {
      setBtnLoading(false);
    }
  }

  codeInputs.forEach((input, i) => {
    input.addEventListener("input", (e) => {
      const val = e.target.value.replace(/\D/g, "");
      input.value = val ? val[0] : "";
      input.classList.toggle("filled", !!input.value);
      input.classList.remove("error-box");
      setStatus("", "");

      if (input.value && i < 5) codeInputs[i + 1].focus();

      const full = codeInputs.map(c => c.value).join("");
      if (full.length === 6) handleVerify(full);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && i > 0) {
        codeInputs[i - 1].value = "";
        codeInputs[i - 1].classList.remove("filled");
        codeInputs[i - 1].focus();
      }
    });

    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const paste = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
      if (paste.length === 6) {
        paste.split("").forEach((d, idx) => {
          codeInputs[idx].value = d;
          codeInputs[idx].classList.add("filled");
        });
        handleVerify(paste);
      }
    });
  });

  async function handleVerify(input) {
    setCodeDisabled(true);
    setStatus("Verifying...", "info");
    await new Promise(r => setTimeout(r, 600));

    if (input === correctCode) {
      stopCountdown();
      clearResendTimer();
      showStep("step-success");
    } else {
      setStatus("Incorrect code. Please try again.", "err");
      codeInputs.forEach(c => c.classList.add("error-box"));
      shakeCard();
      setTimeout(() => {
        clearCodeInputs();
        setCodeDisabled(false);
        codeInputs[0].focus();
      }, 400);
    }
  }

  function startCountdown(seconds) {
    stopCountdown();
    let remaining = seconds;
    timerBar.style.background = "#38bdf8";
    timerBar.style.width = "100%";
    timerInterval = setInterval(() => {
      remaining--;
      timerBar.style.width = (remaining / seconds * 100) + "%";
      if (remaining <= 20) timerBar.style.background = "#f87171";
      if (remaining <= 0) {
        stopCountdown();
        setStatus("Code expired. Please request a new one.", "err");
        setCodeDisabled(true);
      }
    }, 1000);
  }

  function stopCountdown() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  async function handleResend() {
    if (resendBtn.disabled) return;
    clearCodeInputs();
    setCodeDisabled(false);
    setStatus("Sending new code...", "info");
    resendBtn.disabled = true;
    correctCode = generateCode();
    const email = document.getElementById("email-display").textContent;
    try {
      await sendEmail(email, correctCode);
      setStatus("New code sent!", "ok");
      setTimeout(() => setStatus("", ""), 2500);
      startCountdown(120);
      startResendTimer(30);
      codeInputs[0].focus();
    } catch {
      setStatus("Failed to resend. Try again.", "err");
      resendBtn.disabled = false;
    }
  }

  function startResendTimer(s) {
    clearResendTimer();
    let t = s;
    resendBtn.disabled = true;
    resendBtn.textContent = `Resend in ${t}s`;
    resendInterval = setInterval(() => {
      t--;
      if (t <= 0) {
        clearResendTimer();
        resendBtn.disabled = false;
        resendBtn.textContent = "Resend code";
      } else {
        resendBtn.textContent = `Resend in ${t}s`;
      }
    }, 1000);
  }

  function clearResendTimer() {
    if (resendInterval) {
      clearInterval(resendInterval);
      resendInterval = null;
    }
    resendBtn.textContent = "Resend code";
  }

  function showEmailError(msg) {
    emailErrorText.textContent = msg;
    emailError.classList.add("visible");
    emailInput.classList.add("error");
    emailInput.classList.remove("valid");
  }

  function clearEmailError() {
    emailError.classList.remove("visible");
    emailInput.classList.remove("error");
  }

  function setStatus(msg, type) {
    statusMsg.textContent = msg;
    statusMsg.className = "status-msg" + (type ? ` ${type}` : "");
  }

  function setBtnLoading(on) {
    sendBtn.disabled = on;
    sendBtn.innerHTML = on ? '<span class="spinner"></span>' : "Send verification code →";
  }

  function clearCodeInputs() {
    codeInputs.forEach(c => {
      c.value = "";
      c.classList.remove("filled", "error-box");
    });
    setStatus("", "");
  }

  function setCodeDisabled(on) {
    codeInputs.forEach(c => c.disabled = on);
  }

  function goBack() {
    stopCountdown();
    clearResendTimer();
    emailInput.classList.remove("valid");
    showStep("step-email");
    setTimeout(() => emailInput.focus(), 150);
  }

  function resetFlow() {
    stopCountdown();
    clearResendTimer();
    emailInput.value = "";
    emailInput.classList.remove("valid", "error");
    correctCode = "";
    clearCodeInputs();
    showStep("step-email");
    setTimeout(() => emailInput.focus(), 150);
  }

  emailInput.addEventListener("keydown", e => {
    if (e.key === "Enter") handleSendCode();
  });

  emailInput.addEventListener("input", () => {
    clearEmailError();
    emailInput.classList.remove("valid");
  });
