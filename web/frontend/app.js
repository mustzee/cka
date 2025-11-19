// CKA 시뮬레이터 Web App

const API_BASE_URL = 'http://localhost:8000';

let selectedType = 'A';
let currentSession = null;
let timerInterval = null;
let startTime = null;

// 초기화
document.addEventListener('DOMContentLoaded', async () => {
    await loadQuestionTypes();
});

// 문제 타입 로드
async function loadQuestionTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/questions/types`);
        const types = await response.json();

        const typeSelector = document.getElementById('typeSelector');
        typeSelector.innerHTML = '';

        types.forEach(type => {
            const card = document.createElement('div');
            card.className = `type-card ${type.type === 'A' ? 'selected' : ''}`;
            card.onclick = () => selectType(type.type);

            card.innerHTML = `
                <h3>Type ${type.type}</h3>
                <p class="description">${type.description}</p>
                <div class="stats">
                    <span>문제: ${type.question_count}개</span>
                    <span>배점: ${type.total_weight}점</span>
                </div>
            `;

            typeSelector.appendChild(card);
        });
    } catch (error) {
        console.error('타입 로드 실패:', error);
        alert('서버 연결 실패. 백엔드 서버가 실행 중인지 확인하세요.');
    }
}

// 타입 선택
function selectType(type) {
    selectedType = type;
    document.querySelectorAll('.type-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

// 시험 시작
async function startExam() {
    const practiceMode = document.getElementById('practiceModeCheckbox').checked;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/exam/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                exam_type: selectedType,
                practice_mode: practiceMode
            })
        });

        const data = await response.json();
        currentSession = data;

        // 문제 목록 표시
        displayQuestions(data.questions);

        // 화면 전환
        document.getElementById('startScreen').classList.add('hidden');
        document.getElementById('examScreen').classList.remove('hidden');

        // 타이머 시작 (연습 모드 아니면)
        if (!practiceMode) {
            startTimer(120 * 60); // 2시간
        }

    } catch (error) {
        console.error('시험 시작 실패:', error);
        alert('시험 시작에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 문제 표시
function displayQuestions(questions) {
    const questionList = document.getElementById('questionList');
    questionList.innerHTML = '<h3>문제 목록</h3>';

    questions.forEach((q, index) => {
        const questionItem = document.createElement('div');
        questionItem.className = 'question-item';
        questionItem.innerHTML = `
            <h4>${index + 1}. ${q.title}</h4>
            <div class="meta">
                도메인: ${q.domain} | 난이도: ${q.difficulty} | 배점: ${q.weight}점
            </div>
            <div style="margin-top: 10px;">
                <strong>설명:</strong><br>
                <pre style="white-space: pre-wrap; font-family: inherit;">${q.description || ''}</pre>
            </div>
            <div style="margin-top: 10px;">
                <strong>작업:</strong><br>
                <pre style="white-space: pre-wrap; font-family: inherit;">${q.task || ''}</pre>
            </div>
        `;
        questionList.appendChild(questionItem);
    });
}

// 타이머 시작
function startTimer(seconds) {
    startTime = Date.now();
    const endTime = startTime + (seconds * 1000);

    const timerDisplay = document.getElementById('timerDisplay');
    const timerText = document.getElementById('timerText');
    timerDisplay.classList.remove('hidden');

    timerInterval = setInterval(() => {
        const now = Date.now();
        const remaining = Math.max(0, Math.floor((endTime - now) / 1000));

        const hours = Math.floor(remaining / 3600);
        const minutes = Math.floor((remaining % 3600) / 60);
        const secs = remaining % 60;

        timerText.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

        // 10분 남았을 때 경고
        if (remaining <= 600 && remaining > 0) {
            timerDisplay.classList.add('warning');
        }

        // 시간 종료
        if (remaining === 0) {
            clearInterval(timerInterval);
            alert('시험 시간이 종료되었습니다!');
            finishExam();
        }
    }, 1000);
}

// 시험 종료 및 채점
async function finishExam() {
    if (!currentSession) return;

    if (!confirm('시험을 종료하고 채점하시겠습니까?')) {
        return;
    }

    // 타이머 중지
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    document.getElementById('timerDisplay').classList.add('hidden');

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/exam/grade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSession.session_id,
                questions: currentSession.questions
            })
        });

        const result = await response.json();

        // 결과 표시
        displayResults(result);

        // 화면 전환
        document.getElementById('examScreen').classList.add('hidden');
        document.getElementById('resultScreen').classList.remove('hidden');

    } catch (error) {
        console.error('채점 실패:', error);
        alert('채점에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 결과 표시
function displayResults(result) {
    const scoreDisplay = document.getElementById('scoreDisplay');
    const passed = result.passed;

    scoreDisplay.innerHTML = `
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 4em; margin-bottom: 20px;">
                ${passed ? '🎉' : '😔'}
            </div>
            <h2 style="color: ${passed ? '#28a745' : '#dc3545'}; margin-bottom: 10px;">
                ${passed ? '합격!' : '불합격'}
            </h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${result.percentage}%;">
                    ${result.percentage.toFixed(1)}%
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">${result.total_score.toFixed(1)}</div>
                    <div class="label">획득 점수</div>
                </div>
                <div class="stat-box">
                    <div class="number">${result.total_weight}</div>
                    <div class="label">총점</div>
                </div>
                <div class="stat-box">
                    <div class="number">${result.results.filter(r => r.passed).length}</div>
                    <div class="label">정답 문제</div>
                </div>
                <div class="stat-box">
                    <div class="number">${result.results.filter(r => !r.passed).length}</div>
                    <div class="label">오답 문제</div>
                </div>
            </div>
        </div>
    `;

    // 문제별 결과
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '<h3>문제별 결과</h3>';

    result.results.forEach((r, index) => {
        const resultCard = document.createElement('div');
        resultCard.className = `result-card ${r.passed ? '' : 'failed'}`;
        resultCard.innerHTML = `
            <h4>${r.passed ? '✅' : '❌'} ${index + 1}. ${r.title}</h4>
            <div class="meta">
                점수: ${r.score.toFixed(1)}/${r.weight} |
                체크: ${r.passed_checks}/${r.total_checks}
            </div>
            ${!r.passed ? `
                <div style="margin-top: 10px; color: #dc3545;">
                    <strong>오답 상세:</strong><br>
                    ${r.details.filter(d => !d.passed).map(d => `
                        ❌ ${d.check}: ${d.message}
                    `).join('<br>')}
                </div>
            ` : ''}
        `;
        resultsList.appendChild(resultCard);
    });
}

// 통계 보기
async function viewStatistics() {
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/statistics`);
        const stats = await response.json();

        displayStatistics(stats);

        // 모든 화면 숨기기
        document.getElementById('startScreen').classList.add('hidden');
        document.getElementById('examScreen').classList.add('hidden');
        document.getElementById('resultScreen').classList.add('hidden');
        document.getElementById('statsScreen').classList.remove('hidden');

    } catch (error) {
        console.error('통계 로드 실패:', error);
        alert('통계를 불러올 수 없습니다.');
    } finally {
        showLoading(false);
    }
}

// 통계 표시
function displayStatistics(stats) {
    const statsDisplay = document.getElementById('statsDisplay');

    statsDisplay.innerHTML = `
        <div class="stats-grid">
            <div class="stat-box">
                <div class="number">${stats.total_exams}</div>
                <div class="label">총 시험 횟수</div>
            </div>
            <div class="stat-box">
                <div class="number">${stats.passed}</div>
                <div class="label">합격 횟수</div>
            </div>
            <div class="stat-box">
                <div class="number">${stats.failed}</div>
                <div class="label">불합격 횟수</div>
            </div>
            <div class="stat-box">
                <div class="number">${stats.pass_rate.toFixed(1)}%</div>
                <div class="label">합격률</div>
            </div>
        </div>

        <div style="margin-top: 30px;">
            <h3>타입별 통계</h3>
            ${Object.entries(stats.by_type || {}).map(([type, data]) => `
                <div class="card" style="margin: 10px 0;">
                    <h4>Type ${type}</h4>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                        <div>총 ${data.total}회</div>
                        <div style="color: #28a745;">합격 ${data.passed}회</div>
                        <div style="color: #dc3545;">불합격 ${data.failed}회</div>
                        <div>평균 ${data.avg_percentage.toFixed(1)}%</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// 초기화 (새 시험)
function resetExam() {
    // 타이머 정리
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    // 세션 초기화
    currentSession = null;

    // 화면 초기화
    document.getElementById('startScreen').classList.remove('hidden');
    document.getElementById('examScreen').classList.add('hidden');
    document.getElementById('resultScreen').classList.add('hidden');
    document.getElementById('statsScreen').classList.add('hidden');
    document.getElementById('timerDisplay').classList.add('hidden');

    // 타입 다시 로드
    loadQuestionTypes();
}

// 로딩 표시
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}
