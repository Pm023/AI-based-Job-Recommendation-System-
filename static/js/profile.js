/**
 * CareerMatch AI - Profile & Resume Upload Script
 */
document.addEventListener('DOMContentLoaded', function() {
    const addSkillBtn = document.getElementById('add-skill-btn');
    const skillsContainer = document.getElementById('skills-container');

    if (addSkillBtn && skillsContainer) {
        addSkillBtn.addEventListener('click', function() {
            const newRow = document.createElement('div');
            newRow.className = 'row g-2 align-items-center mb-2 skill-entry-row';
            newRow.innerHTML = `
                <div class="col-md-6">
                    <input type="text" name="skill_name" class="form-control" placeholder="e.g. Python, SQL, Docker" required>
                </div>
                <div class="col-md-4">
                    <select name="skill_proficiency" class="form-select">
                        <option value="Beginner">Beginner</option>
                        <option value="Basic">Basic</option>
                        <option value="Intermediate" selected>Intermediate</option>
                        <option value="Advanced">Advanced</option>
                        <option value="Expert">Expert</option>
                    </select>
                </div>
                <div class="col-md-2 text-center">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-skill-btn">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
            skillsContainer.appendChild(newRow);
        });

        skillsContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-skill-btn')) {
                const row = e.target.closest('.skill-entry-row');
                if (skillsContainer.querySelectorAll('.skill-entry-row').length > 1) {
                    row.remove();
                } else {
                    alert('You must maintain at least one skill entry.');
                }
            }
        });
    }

    // Resume Upload AJAX handler
    const resumeForm = document.getElementById('resume-upload-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(resumeForm);
            const statusDiv = document.getElementById('resume-status');
            const resultBox = document.getElementById('extracted-skills-result');
            const skillsListDiv = document.getElementById('detected-skills-list');

            statusDiv.innerHTML = `
                <div class="alert alert-info d-flex align-items-center gap-2">
                    <div class="spinner-border spinner-border-sm" role="status"></div>
                    <div>Analyzing resume text via NLP pipeline (Cleaning, Tokenization, Lemmatization & Skill Dictionary Mapping)...</div>
                </div>
            `;
            statusDiv.classList.remove('d-none');
            resultBox.classList.add('d-none');

            fetch('/api/analyze-resume', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = `
                        <div class="alert alert-success">
                            <i class="bi bi-check-circle-fill me-2"></i>
                            <strong>Resume Analyzed!</strong> Detected ${data.total_found} skills from your resume.
                        </div>
                    `;

                    skillsListDiv.innerHTML = '';
                    if (data.extracted_skills && data.extracted_skills.length > 0) {
                        data.extracted_skills.forEach((sk, idx) => {
                            const item = document.createElement('div');
                            item.className = 'col-md-6 mb-2';
                            item.innerHTML = `
                                <div class="card p-2 border shadow-sm flex-row align-items-center justify-content-between">
                                    <div>
                                        <strong>${sk.name}</strong>
                                        <small class="text-muted d-block">${sk.category}</small>
                                    </div>
                                    <select class="form-select form-select-sm confirmed-skill-prof" style="width:120px;" data-name="${sk.name}" data-category="${sk.category}">
                                        <option value="Beginner">Beginner</option>
                                        <option value="Basic">Basic</option>
                                        <option value="Intermediate" selected>Intermediate</option>
                                        <option value="Advanced">Advanced</option>
                                        <option value="Expert">Expert</option>
                                    </select>
                                </div>
                            `;
                            skillsListDiv.appendChild(item);
                        });
                    } else {
                        skillsListDiv.innerHTML = '<div class="alert alert-warning">No specific skills detected automatically. You can manually enter your skills in Profile Setup.</div>';
                    }

                    resultBox.classList.remove('d-none');
                } else {
                    statusDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            ${data.error || 'Parsing error encountered.'}
                        </div>
                    `;
                }
            })
            .catch(err => {
                statusDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        Server connection error. Please try again or manually enter your skills.
                    </div>
                `;
            });
        });

        // Save Confirmed Skills Button
        const saveConfirmedBtn = document.getElementById('save-confirmed-skills-btn');
        if (saveConfirmedBtn) {
            saveConfirmedBtn.addEventListener('click', function() {
                const selects = document.querySelectorAll('.confirmed-skill-prof');
                const skillsToSave = [];

                selects.forEach(sel => {
                    skillsToSave.push({
                        name: sel.getAttribute('data-name'),
                        category: sel.getAttribute('data-category'),
                        proficiency: sel.value
                    });
                });

                fetch('/api/confirm-extracted-skills', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ skills: skillsToSave })
                })
                .then(res => res.json())
                .then(resData => {
                    if (resData.success) {
                        alert(resData.message);
                        window.location.href = '/dashboard';
                    }
                });
            });
        }
    }
});
