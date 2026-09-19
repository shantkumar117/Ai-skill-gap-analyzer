document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.querySelector("textarea[name='current_skills']");
  document.querySelectorAll("[data-skill]").forEach((button) => {
    button.addEventListener("click", () => {
      const skill = button.dataset.skill;
      const skills = textarea.value.split(",").map((item) => item.trim()).filter(Boolean);
      if (!skills.some((item) => item.toLowerCase() === skill.toLowerCase())) {
        textarea.value = skills.concat(skill).join(", ");
      }
      textarea.focus();
    });
  });

  const chart = document.getElementById("skillChart");
  if (chart && window.Chart) {
    new Chart(chart, {
      type: "doughnut",
      data: {
        labels: ["Skills you have", "Skills to build"],
        datasets: [{ data: [Number(chart.dataset.have), Number(chart.dataset.missing)], backgroundColor: ["#55b88b", "#f47c50"], borderWidth: 0 }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: "70%", plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 20, font: { family: "DM Sans" } } } } }
    });
  }
});
