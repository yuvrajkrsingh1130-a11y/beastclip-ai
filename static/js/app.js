// BeastClip AI Client Application Logic
let currentJobId = null;
let pollInterval = null;
let currentClipsMap = {};
let activeVoiceClipId = null;
let activePublishClipId = null;
let activeEditClipId = null;
let mediaRecorder = null;
let audioChunks = [];
let recordedBlob = null;
let connectedChannelData = null;

const PRESET_CREATOR_URLS = {
    ishowspeed: {
        url: "https://www.youtube.com/@IShowSpeed",
        tag: "@IShowSpeed"
    },
    kaicenat: {
        url: "https://www.youtube.com/@KaiCenat",
        tag: "@KaiCenat"
    },
    jynxzi: {
        url: "https://www.youtube.com/@Jynxzi",
        tag: "@Jynxzi"
    },
    caseoh: {
        url: "https://www.youtube.com/@CaseOh",
        tag: "@CaseOh"
    }
};

document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();
    initPresets();
    initEventListeners();
    checkYouTubeStatus();
});

function initPresets() {
    document.querySelectorAll(".preset-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const key = btn.getAttribute("data-preset");
            selectStreamerPreset(key, btn);
        });
    });
}

async function selectStreamerPreset(key, btnElement) {
    try {
        // Highlight active preset button
        document.querySelectorAll(".preset-btn").forEach(b => {
            b.classList.remove("ring-2", "ring-indigo-500", "bg-indigo-600/30", "border-indigo-400");
        });
        if (btnElement) {
            btnElement.classList.add("ring-2", "ring-indigo-500", "bg-indigo-600/30", "border-indigo-400");
        }

        // Fetch streamer metadata + top viral streams from backend
        const res = await fetch(`/api/streamer-preset/${key}`);
        if (!res.ok) throw new Error("Could not fetch streamer preset");
        const data = await res.json();

        // 1. Auto-fill Creator Credit Handle
        const creditInput = document.getElementById("creatorCreditInput");
        if (creditInput && data.handle) {
            creditInput.value = data.handle;
        }

        // 2. Auto-select Recommended Subtitle Style
        if (data.recommended_style) {
            const styleRadio = document.querySelector(`input[name="subtitleStyle"][value="${data.recommended_style}"]`);
            if (styleRadio) {
                styleRadio.checked = true;
                styleRadio.dispatchEvent(new Event("change"));
            }
        }

        // 3. Auto-select Recommended Layout (Split Screen)
        if (data.recommended_layout) {
            const layoutRadio = document.querySelector(`input[name="layout"][value="${data.recommended_layout}"]`);
            if (layoutRadio) {
                layoutRadio.checked = true;
                layoutRadio.dispatchEvent(new Event("change"));
            }
        }

        // 4. Auto-populate URL and Video Preview with the #1 Top Viral Stream
        const bestVid = data.best_video || (data.videos && data.videos[0]);
        if (bestVid) {
            applyStreamerVideo(bestVid, data.handle);
        }

        // 5. Render Stream Selection Chips Strip
        renderStreamerStreamsList(data);

        showToast(`⚡ Loaded top clip-ready stream for ${data.name}!`);

    } catch (e) {
        console.error("Preset load error:", e);
        const fallback = PRESET_CREATOR_URLS[key];
        if (fallback) {
            document.getElementById("videoUrlInput").value = fallback.url;
            document.getElementById("creatorCreditInput").value = fallback.tag;
            showToast(`Loaded ${key} preset`);
        }
    }
}

function applyStreamerVideo(vid, creditHandle) {
    const urlInput = document.getElementById("videoUrlInput");
    if (urlInput) {
        urlInput.value = vid.url;
    }

    // Update live video preview card
    const infoCard = document.getElementById("videoInfoCard");
    const thumbImg = document.getElementById("videoThumbImg");
    const titleLabel = document.getElementById("videoTitleLabel");
    const metaLabel = document.getElementById("videoMetaLabel");

    if (infoCard && thumbImg && titleLabel && metaLabel) {
        thumbImg.src = vid.thumbnail || `https://i.ytimg.com/vi/${vid.id}/hqdefault.jpg`;
        titleLabel.textContent = vid.title || "Stream Highlight";
        titleLabel.title = vid.title || "";
        metaLabel.textContent = `${vid.duration || 'Stream'} • ${creditHandle || '@Streamer'} • ${vid.badge || 'Viral Pick'}`;
        infoCard.classList.remove("hidden");
    }
}

function renderStreamerStreamsList(data) {
    const container = document.getElementById("streamerStreamsContainer");
    const list = document.getElementById("streamerStreamsList");
    const heading = document.getElementById("streamerStreamsHeading");
    if (!container || !list) return;

    if (heading) {
        heading.innerHTML = `<i data-lucide="flame" class="w-3.5 h-3.5 text-yellow-400"></i> Top Viral Streams for ${data.name}`;
    }

    list.innerHTML = "";
    (data.videos || []).forEach((vid, idx) => {
        const isSelected = (idx === 0);
        const item = document.createElement("div");
        item.className = `stream-chip flex items-center gap-2.5 p-2 rounded-lg bg-black/40 hover:bg-indigo-600/20 border ${isSelected ? 'border-indigo-500 bg-indigo-950/40' : 'border-white/5'} cursor-pointer transition text-left`;
        item.innerHTML = `
            <img src="${vid.thumbnail || 'https://i.ytimg.com/vi/' + vid.id + '/hqdefault.jpg'}" class="w-14 h-9 object-cover rounded flex-shrink-0" />
            <div class="min-w-0 flex-1">
                <div class="text-[11px] font-bold text-white truncate">${vid.title}</div>
                <div class="text-[9px] text-gray-400 flex items-center gap-1.5 mt-0.5">
                    <span class="text-yellow-400 font-semibold">${vid.badge || 'Viral'}</span>
                    <span>•</span>
                    <span>${vid.duration || 'Stream'}</span>
                </div>
            </div>
            <button type="button" class="px-2 py-1 rounded ${isSelected ? 'bg-indigo-600 text-white' : 'bg-white/5 text-gray-300 hover:bg-indigo-600/40 hover:text-white'} text-[10px] font-bold transition flex-shrink-0">
                ${isSelected ? 'Active' : 'Clip This'}
            </button>
        `;
        item.addEventListener("click", () => {
            // Unhighlight all other chips
            list.querySelectorAll(".stream-chip").forEach(c => {
                c.classList.remove("border-indigo-500", "bg-indigo-950/40");
                c.classList.add("border-white/5");
                const b = c.querySelector("button");
                if (b) {
                    b.className = "px-2 py-1 rounded bg-white/5 text-gray-300 hover:bg-indigo-600/40 hover:text-white text-[10px] font-bold transition flex-shrink-0";
                    b.textContent = "Clip This";
                }
            });

            // Highlight clicked chip
            item.classList.remove("border-white/5");
            item.classList.add("border-indigo-500", "bg-indigo-950/40");
            const btn = item.querySelector("button");
            if (btn) {
                btn.className = "px-2 py-1 rounded bg-indigo-600 text-white text-[10px] font-bold transition flex-shrink-0";
                btn.textContent = "Active";
            }

            applyStreamerVideo(vid, data.handle);
            showToast(`Switched stream: ${vid.title.substring(0, 28)}...`);
        });
        list.appendChild(item);
    });

    container.classList.remove("hidden");
    lucide.createIcons();
}

function initEventListeners() {
    // Mode Switcher Tabs (Single vs Multi-Video Compilation)
    document.getElementById("modeTabSingle")?.addEventListener("click", () => switchStudioMode("single"));
    document.getElementById("modeTabMulti")?.addEventListener("click", () => switchStudioMode("multi"));

    // Multi-video dynamic inputs
    document.getElementById("addMultiUrlBtn")?.addEventListener("click", addMultiUrlInputRow);
    document.getElementById("fetchMultiHandlesBtn")?.addEventListener("click", fetchMultiVideoHandles);
    document.getElementById("generateCompilationBtn")?.addEventListener("click", startMultiVideoCompilation);
    document.getElementById("stitchCompilationBtn")?.addEventListener("click", stitchGalleryClipsIntoCompilation);

    // Multi-video container per-row handle buttons
    document.getElementById("multiUrlInputsContainer")?.addEventListener("click", (e) => {
        const fetchBtn = e.target.closest(".fetch-row-handle-btn");
        if (fetchBtn) {
            const row = fetchBtn.closest(".multi-url-row");
            if (row) fetchSingleRowHandle(row, fetchBtn);
        }
    });

    // Fetch info button
    document.getElementById("fetchInfoBtn").addEventListener("click", fetchVideoInfo);

    // Generate clips button
    document.getElementById("generateBtn").addEventListener("click", startClipGeneration);

    // Edit Metadata Modal triggers
    document.getElementById("closeEditModalBtn")?.addEventListener("click", closeEditMetadataModal);
    document.getElementById("cancelEditModalBtn")?.addEventListener("click", closeEditMetadataModal);
    document.getElementById("saveEditModalBtn")?.addEventListener("click", saveEditedMetadata);
    document.getElementById("editTitleInput")?.addEventListener("input", (e) => {
        document.getElementById("editTitleCharCount").innerText = `${e.target.value.length}/100`;
    });
    document.getElementById("copyPinnedCommentBtn")?.addEventListener("click", () => {
        const val = document.getElementById("editPinnedCommentInput")?.value || "";
        if (val) {
            navigator.clipboard.writeText(val).then(() => showToast("Pinned Comment Copied!"));
        }
    });
    document.getElementById("copyFullPackageModalBtn")?.addEventListener("click", () => {
        if (!activeEditClipId) return;
        copyClipField(activeEditClipId, "viral_package");
    });
    document.querySelectorAll(".trending-tag-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            const tag = pill.getAttribute("data-tag");
            const tagsInput = document.getElementById("editTagsInput");
            if (tag && tagsInput) {
                const current = tagsInput.value.trim();
                if (!current.includes(tag)) {
                    tagsInput.value = current ? `${current} ${tag}` : tag;
                    showToast(`Added ${tag}`);
                } else {
                    showToast(`${tag} already added`);
                }
            }
        });
    });

    // YouTube Auth Modal triggers
    document.getElementById("ytChannelBadge").addEventListener("click", () => {
        document.getElementById("ytAuthModal").classList.remove("hidden");
    });
    document.getElementById("closeYtModalBtn").addEventListener("click", () => {
        document.getElementById("ytAuthModal").classList.add("hidden");
    });
    document.getElementById("saveYtCredsBtn").addEventListener("click", setupYouTubeAuth);

    // YouTube Single Publish Modal triggers
    document.getElementById("closeYtPublishModalBtn").addEventListener("click", closePublishModal);
    document.getElementById("closeYtSuccessModalBtn").addEventListener("click", closePublishModal);
    document.getElementById("confirmPublishBtn").addEventListener("click", submitPublishShort);

    // Timing mode toggles (Now vs Auto vs Manual)
    document.querySelectorAll('input[name="publishTimingMode"]').forEach(radio => {
        radio.addEventListener("change", onTimingModeChanged);
    });

    // Quick Schedule Pills
    document.querySelectorAll(".sched-pill").forEach(pill => {
        pill.addEventListener("click", () => applySchedulePreset(pill));
    });

    // Title Char Count
    document.getElementById("publishTitleInput").addEventListener("input", (e) => {
        document.getElementById("publishTitleCharCount").innerText = `${e.target.value.length}/100`;
    });

    // YouTube Batch Schedule Modal triggers
    document.getElementById("dripScheduleAllBtn").addEventListener("click", openBatchScheduleModal);
    document.getElementById("closeYtBatchModalBtn").addEventListener("click", closeBatchScheduleModal);
    document.getElementById("closeBatchResultsBtn").addEventListener("click", closeBatchScheduleModal);
    document.getElementById("confirmBatchScheduleBtn").addEventListener("click", submitBatchSchedule);
    document.getElementById("batchStartDatetime").addEventListener("change", updateBatchSchedulePreview);
    document.getElementById("batchCadenceSelect").addEventListener("change", updateBatchSchedulePreview);

    document.querySelectorAll('input[name="batchMode"]').forEach(radio => {
        radio.addEventListener("change", onBatchModeChanged);
    });

    // Voice Modal triggers & Preview
    document.getElementById("previewVoiceBtn")?.addEventListener("click", previewTtsVoiceover);
    document.getElementById("closeVoiceModalBtn").addEventListener("click", () => {
        document.getElementById("voiceModal").classList.add("hidden");
        const audio = document.getElementById("voicePreviewAudio");
        if (audio) audio.pause();
    });

    // Mic recording
    document.getElementById("recordMicBtn").addEventListener("click", toggleMicRecording);
    document.getElementById("applyMicBtn").addEventListener("click", submitMicVoiceover);
    document.getElementById("applyTtsBtn").addEventListener("click", submitTtsVoiceover);

    // Auto Fetch Handle button
    document.getElementById("autoFetchHandleBtn")?.addEventListener("click", autoFetchCreatorHandle);
}

// ==================== MODE SWITCHING & MULTI-VIDEO COMPILATIONS ====================

let activeStudioMode = "single";

function switchStudioMode(mode) {
    activeStudioMode = mode;
    const btnSingle = document.getElementById("modeTabSingle");
    const btnMulti = document.getElementById("modeTabMulti");
    const panelSingle = document.getElementById("singleVideoPanel");
    const panelMulti = document.getElementById("multiVideoPanel");
    const singleClipSettings = document.getElementById("singleModeClipSettings");
    const singleGenBox = document.getElementById("singleGenerateBox");
    const multiGenBox = document.getElementById("multiGenerateBox");

    if (mode === "multi") {
        btnSingle.className = "py-2.5 px-3 rounded-xl text-xs font-bold text-gray-400 hover:text-white transition flex items-center justify-center gap-2";
        btnMulti.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 bg-gradient-to-r from-yellow-500 to-amber-500 text-black font-extrabold shadow-md";
        
        panelSingle.classList.add("hidden");
        panelMulti.classList.remove("hidden");
        singleClipSettings.classList.add("hidden");
        singleGenBox.classList.add("hidden");
        multiGenBox.classList.remove("hidden");
    } else {
        btnSingle.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md";
        btnMulti.className = "py-2.5 px-3 rounded-xl text-xs font-bold text-gray-400 hover:text-white transition flex items-center justify-center gap-1.5";
        
        panelSingle.classList.remove("hidden");
        panelMulti.classList.add("hidden");
        singleClipSettings.classList.remove("hidden");
        singleGenBox.classList.remove("hidden");
        multiGenBox.classList.add("hidden");
    }
}

function addMultiUrlInputRow() {
    const container = document.getElementById("multiUrlInputsContainer");
    const rows = container.querySelectorAll(".multi-url-row");
    if (rows.length >= 5) {
        showToast("Maximum 5 videos allowed for a Top Compilation");
        return;
    }

    const nextIndex = rows.length + 1;
    const row = document.createElement("div");
    row.className = "multi-url-row space-y-1.5 p-2.5 rounded-xl bg-white/[0.03] border border-white/5";
    row.innerHTML = `
        <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-yellow-400 w-12 font-mono flex-shrink-0">Vid #${nextIndex}:</span>
            <input type="text" placeholder="https://www.youtube.com/watch?v=..." 
                class="multi-url-input flex-1 bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-yellow-500">
            <button type="button" class="fetch-row-handle-btn p-2 rounded-lg bg-yellow-500/10 hover:bg-yellow-500/25 text-yellow-400 border border-yellow-500/30 transition flex-shrink-0" title="Auto-detect handle for Vid #${nextIndex}">
                <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
            </button>
            <button type="button" class="p-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/25 text-rose-400 border border-rose-500/30 transition flex-shrink-0" title="Remove URL" onclick="removeMultiUrlRow(this)">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            </button>
        </div>
        <div class="flex items-center gap-2 pl-14">
            <input type="text" placeholder="Ladder Label: e.g. moment #${nextIndex} 🔥"
                class="multi-clip-label flex-1 bg-black/30 border border-white/5 rounded-lg px-2.5 py-1.5 text-[11px] text-gray-200 focus:outline-none focus:border-yellow-500">
        </div>
        <div class="row-creator-chip hidden flex items-center gap-1.5 text-[10px] pl-14">
            <span class="text-yellow-300 font-semibold font-mono channel-tag">@Creator</span>
            <span class="text-gray-500">•</span>
            <span class="video-title-snip truncate max-w-[240px] text-gray-400">Title</span>
        </div>
    `;
    container.appendChild(row);
    lucide.createIcons();
}

function removeMultiUrlRow(btn) {
    const row = btn.closest(".multi-url-row");
    if (row) {
        row.remove();
        const rows = document.querySelectorAll("#multiUrlInputsContainer .multi-url-row");
        rows.forEach((r, idx) => {
            const label = r.querySelector("span.font-mono");
            if (label) label.innerText = `Vid #${idx + 1}:`;
        });
        syncMultiHandlesToCreditInput();
    }
}

async function fetchSingleRowHandle(rowEl, btnEl) {
    const input = rowEl.querySelector(".multi-url-input");
    const url = input?.value.trim();
    if (!url) {
        showToast("Please enter a YouTube URL in this field first!");
        return;
    }

    if (btnEl) {
        btnEl.disabled = true;
        btnEl.innerHTML = `<div class="w-3 h-3 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>`;
    }

    try {
        const res = await fetch("/api/extract-info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        if (res.ok && data.uploader) {
            const handle = `@${data.uploader.replace(/\s+/g, '')}`;
            const chip = rowEl.querySelector(".row-creator-chip");
            if (chip) {
                chip.querySelector(".channel-tag").innerText = handle;
                chip.querySelector(".video-title-snip").innerText = data.title || "Highlight";
                chip.classList.remove("hidden");
            }
            
            // Auto fill ladder label if empty
            const labelInput = rowEl.querySelector(".multi-clip-label");
            if (labelInput && !labelInput.value.trim()) {
                const words = (data.title || "").replace(/[^a-zA-Z0-9\s]/g, '').split(/\s+/).filter(Boolean);
                labelInput.value = words.slice(0, 3).join(" ").toLowerCase() || "insane moment 🔥";
            }

            syncMultiHandlesToCreditInput();
            showToast(`Detected: ${handle}`);
        } else {
            showToast("Could not detect creator handle");
        }
    } catch (e) {
        console.error("fetchSingleRowHandle error:", e);
        showToast("Error detecting handle");
    } finally {
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5"></i>`;
            lucide.createIcons();
        }
    }
}

async function fetchMultiVideoHandles() {
    const container = document.getElementById("multiUrlInputsContainer");
    const rows = container.querySelectorAll(".multi-url-row");
    const urls = [];
    const validRows = [];

    rows.forEach(r => {
        const url = r.querySelector(".multi-url-input")?.value.trim();
        if (url) {
            urls.push(url);
            validRows.push(r);
        }
    });

    if (urls.length === 0) {
        showToast("Please enter at least 1 YouTube video URL first!");
        return;
    }

    const fetchBtn = document.getElementById("fetchMultiHandlesBtn");
    const autoCreditBtn = document.getElementById("autoFetchHandleBtn");
    
    if (fetchBtn) {
        fetchBtn.disabled = true;
        fetchBtn.innerHTML = `<div class="w-3 h-3 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin"></div> Fetching ${urls.length} Handles...`;
    }
    if (autoCreditBtn) {
        autoCreditBtn.disabled = true;
        autoCreditBtn.innerHTML = `<div class="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div> Fetching...`;
    }

    try {
        const res = await fetch("/api/extract-multi-info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ urls })
        });
        const data = await res.json();
        
        if (res.ok && data.results) {
            const handles = [];
            data.results.forEach((info, idx) => {
                const row = validRows[idx];
                if (row && info.uploader) {
                    const handle = `@${info.uploader.replace(/\s+/g, '')}`;
                    handles.push(handle);
                    const chip = row.querySelector(".row-creator-chip");
                    if (chip) {
                        chip.querySelector(".channel-tag").innerText = handle;
                        chip.querySelector(".video-title-snip").innerText = info.title || "Highlight";
                        chip.classList.remove("hidden");
                    }
                    // Auto fill label
                    const labelInput = row.querySelector(".multi-clip-label");
                    if (labelInput && !labelInput.value.trim()) {
                        const words = (info.title || "").replace(/[^a-zA-Z0-9\s]/g, '').split(/\s+/).filter(Boolean);
                        labelInput.value = words.slice(0, 3).join(" ").toLowerCase() || "viral moment 🔥";
                    }
                }
            });

            // Combine unique handles
            const uniqueHandles = [...new Set(handles)];
            if (uniqueHandles.length > 0) {
                document.getElementById("creatorCreditInput").value = uniqueHandles.join(" ");
                showToast(`Auto-fetched ${uniqueHandles.length} creator handles & tags!`);
            } else {
                showToast("Could not detect handles");
            }
        } else {
            showToast("Failed to fetch creator info");
        }
    } catch (e) {
        console.error("fetchMultiVideoHandles error:", e);
        showToast("Network error fetching creator handles");
    } finally {
        if (fetchBtn) {
            fetchBtn.disabled = false;
            fetchBtn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-yellow-400"></i> Auto-Fetch Handles & Tags`;
        }
        if (autoCreditBtn) {
            autoCreditBtn.disabled = false;
            autoCreditBtn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-400"></i> Auto Fetch Handle`;
        }
        lucide.createIcons();
    }
}

function syncMultiHandlesToCreditInput() {
    const chips = document.querySelectorAll("#multiUrlInputsContainer .row-creator-chip:not(.hidden) .channel-tag");
    const handles = [];
    chips.forEach(c => {
        const text = c.innerText.trim();
        if (text && text.startsWith("@")) handles.push(text);
    });
    const unique = [...new Set(handles)];
    if (unique.length > 0) {
        document.getElementById("creatorCreditInput").value = unique.join(" ");
    }
}

async function startMultiVideoCompilation() {
    const inputs = document.querySelectorAll(".multi-url-input");
    const urls = Array.from(inputs).map(i => i.value.trim()).filter(Boolean);

    if (urls.length < 2) {
        alert("Please enter at least 2 YouTube video URLs to create a compilation!");
        return;
    }

    const rankingHeader = document.getElementById("rankingHeaderInput")?.value.trim() || "Ranking Best Fails of The Week";
    const labelInputs = document.querySelectorAll(".multi-clip-label");
    const clipLabels = Array.from(labelInputs).map(i => i.value.trim());

    const targetDuration = parseInt(document.getElementById("compilationDurationSelect").value, 10);
    const countdownStyle = document.getElementById("compilationStyleSelect").value;
    const layout = document.querySelector('input[name="layout"]:checked')?.value || "split_screen";
    const subtitleStyle = document.querySelector('input[name="subStyle"]:checked')?.value || "hormozi";
    const creatorCredit = document.getElementById("creatorCreditInput").value.trim();

    const genBtn = document.getElementById("generateCompilationBtn");
    genBtn.disabled = true;
    genBtn.innerHTML = `<div class="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div> Rendering Ranking Leaderboard Short...`;

    // Show progress card
    const progressCard = document.getElementById("progressCard");
    progressCard.classList.remove("hidden");
    document.getElementById("progressBarFill").style.width = "5%";
    document.getElementById("progressPercent").innerText = "5%";
    document.getElementById("progressStatusText").innerHTML = `<span>Starting Ranking Leaderboard Pipeline...</span>`;

    try {
        const res = await fetch("/api/compilation/create-multi-video", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                urls: urls,
                ranking_header: rankingHeader,
                clip_labels: clipLabels,
                target_duration: targetDuration,
                countdown_style: countdownStyle,
                subtitle_style: subtitleStyle,
                layout: layout,
                creator_credit: creatorCredit || null
            })
        });

        const data = await res.json();
        if (res.ok) {
            currentJobId = data.job_id;
            pollInterval = setInterval(pollJobStatus, 2000);
        } else {
            alert(`Compilation error: ${data.detail}`);
            genBtn.disabled = false;
            genBtn.innerHTML = `<i data-lucide="trophy" class="w-5 h-5"></i> CREATE TOP COUNTDOWN COMPILATION NOW 🏆`;
            lucide.createIcons();
        }
    } catch (e) {
        console.error(e);
        alert("Network error starting compilation pipeline.");
        genBtn.disabled = false;
        genBtn.innerHTML = `<i data-lucide="trophy" class="w-5 h-5"></i> CREATE TOP COUNTDOWN COMPILATION NOW 🏆`;
        lucide.createIcons();
    }
}

async function stitchGalleryClipsIntoCompilation() {
    const clips = Object.values(currentClipsMap);
    if (clips.length < 2) {
        alert("You need at least 2 generated clips in the gallery to stitch a compilation!");
        return;
    }

    const clipIds = clips.map(c => c.clip_id);
    const stitchBtn = document.getElementById("stitchCompilationBtn");
    stitchBtn.disabled = true;
    stitchBtn.innerHTML = `<div class="w-3.5 h-3.5 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin"></div> Stitching...`;

    try {
        const res = await fetch("/api/compilation/stitch-gallery-clips", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                clip_ids: clipIds,
                target_duration: 50,
                countdown_style: "gold"
            })
        });

        const data = await res.json();
        if (res.ok && data.clip) {
            showToast("Successfully Created Top Countdown Compilation!");
            // Prepend compilation to top of gallery
            const updatedClips = [data.clip, ...clips];
            renderGeneratedClips(updatedClips);
        } else {
            alert(`Stitch error: ${data.detail || 'Failed to stitch clips'}`);
        }
    } catch (e) {
        console.error(e);
        alert("Failed to stitch gallery clips.");
    } finally {
        stitchBtn.disabled = false;
        stitchBtn.innerHTML = `<i data-lucide="trophy" class="w-4 h-4 text-yellow-400"></i> <span>Stitch All into Top Compilation</span>`;
        lucide.createIcons();
    }
}

// ==================== INGESTION & PIPELINE ====================

async function autoFetchCreatorHandle() {
    if (currentStudioMode === "multi") {
        await fetchMultiVideoHandles();
        return;
    }

    const url = document.getElementById("videoUrlInput").value.trim();
    if (!url) {
        showToast("Please enter a YouTube video URL first!");
        return;
    }
    const btn = document.getElementById("autoFetchHandleBtn");
    btn.disabled = true;
    btn.innerHTML = `<div class="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div> Fetching...`;

    try {
        const res = await fetch("/api/extract-info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        if (res.ok && data.uploader) {
            const handle = `@${data.uploader.replace(/\s+/g, '')}`;
            document.getElementById("creatorCreditInput").value = handle;
            showToast(`Fetched handle: ${handle}`);
        } else {
            showToast("Could not auto-detect handle");
        }
    } catch (e) {
        console.error(e);
        showToast("Error fetching creator handle");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-400"></i> Auto Fetch Handle`;
        lucide.createIcons();
    }
}

async function fetchVideoInfo() {
    const url = document.getElementById("videoUrlInput").value.trim();
    if (!url) {
        showToast("Please enter a YouTube video URL first!");
        return;
    }

    const btn = document.getElementById("fetchInfoBtn");
    btn.disabled = true;
    btn.innerText = "Loading...";

    try {
        const res = await fetch("/api/extract-info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        const data = await res.json();

        if (res.ok) {
            const durationMins = data.duration ? Math.round(data.duration / 60) : 0;
            document.getElementById("videoTitleLabel").innerText = data.title || "Stream Highlight";
            document.getElementById("videoMetaLabel").innerText = `${data.uploader || 'Creator'} • ${durationMins} mins`;
            if (data.thumbnail) {
                document.getElementById("videoThumbImg").src = data.thumbnail;
            }
            document.getElementById("videoInfoCard").classList.remove("hidden");
            if (data.uploader && !document.getElementById("creatorCreditInput").value) {
                document.getElementById("creatorCreditInput").value = `@${data.uploader.replace(/\s+/g, '')}`;
            }
            showToast("Video info loaded successfully!");
        } else {
            alert(`Error: ${data.detail || 'Could not fetch video info'}`);
        }
    } catch (e) {
        console.error("fetchVideoInfo error:", e);
        showToast("Could not parse video info.");
    } finally {
        btn.disabled = false;
        btn.innerText = "Fetch Info";
    }
}

async function startClipGeneration() {
    const url = document.getElementById("videoUrlInput").value.trim();
    if (!url) {
        alert("Please enter a YouTube URL to clip!");
        return;
    }

    const layout = document.querySelector('input[name="layout"]:checked')?.value || "split_screen";
    const subtitleStyle = document.querySelector('input[name="subStyle"]:checked')?.value || "hormozi";
    const targetDuration = parseInt(document.getElementById("clipDurationSelect").value, 10);
    const numClips = parseInt(document.getElementById("clipCountSelect").value, 10);
    const creatorCredit = document.getElementById("creatorCreditInput").value.trim();
    const enableSeamlessLoop = document.getElementById("seamlessLoopToggle")?.checked ?? true;

    const generateBtn = document.getElementById("generateBtn");
    generateBtn.disabled = true;
    generateBtn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div> Generating...`;

    // Show progress card
    const progressCard = document.getElementById("progressCard");
    progressCard.classList.remove("hidden");
    document.getElementById("progressBarFill").style.width = "5%";
    document.getElementById("progressPercent").innerText = "5%";
    document.getElementById("progressStatusText").innerHTML = `<span>Starting BeastClip AI pipeline...</span>`;

    try {
        const res = await fetch("/api/process-video", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url,
                target_duration: targetDuration,
                num_clips: numClips,
                subtitle_style: subtitleStyle,
                layout: layout,
                creator_credit: creatorCredit || null,
                enable_copyright_shield: true,
                enable_seamless_loop: enableSeamlessLoop
            })
        });

        const data = await res.json();
        if (res.ok) {
            currentJobId = data.job_id;
            pollInterval = setInterval(pollJobStatus, 2000);
        } else {
            alert(`Failed: ${data.detail}`);
            generateBtn.disabled = false;
            generateBtn.innerHTML = `<i data-lucide="zap" class="w-5 h-5"></i> GENERATE VIRAL SHORTS NOW`;
            lucide.createIcons();
        }
    } catch (e) {
        console.error(e);
        alert("Network error starting pipeline.");
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<i data-lucide="zap" class="w-5 h-5"></i> GENERATE VIRAL SHORTS NOW`;
        lucide.createIcons();
    }
}

async function pollJobStatus() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/api/status/${currentJobId}`);
        const job = await res.json();

        if (res.ok) {
            const progress = job.progress || 0;
            document.getElementById("progressBarFill").style.width = `${progress}%`;
            document.getElementById("progressPercent").innerText = `${progress}%`;
            document.getElementById("progressStatusText").innerHTML = `<span>${job.message || 'Processing...'}</span>`;

            if (job.status === "completed") {
                clearInterval(pollInterval);
                document.getElementById("generateBtn").disabled = false;
                document.getElementById("generateBtn").innerHTML = `<i data-lucide="zap" class="w-5 h-5"></i> GENERATE VIRAL SHORTS NOW`;
                lucide.createIcons();
                renderGeneratedClips(job.clips || []);
            } else if (job.status === "failed") {
                clearInterval(pollInterval);
                alert(`Processing failed: ${job.error}`);
                document.getElementById("generateBtn").disabled = false;
                document.getElementById("generateBtn").innerHTML = `<i data-lucide="zap" class="w-5 h-5"></i> GENERATE VIRAL SHORTS NOW`;
                lucide.createIcons();
            }
        }
    } catch (e) {
        console.error("Poll error:", e);
    }
}

function renderGeneratedClips(clips) {
    const grid = document.getElementById("clipsGrid");
    const emptyPlaceholder = document.getElementById("emptyGalleryPlaceholder");
    const countBadge = document.getElementById("clipsCountBadge");

    currentClipsMap = {};

    if (!clips || clips.length === 0) {
        emptyPlaceholder.classList.remove("hidden");
        countBadge.classList.add("hidden");
        document.getElementById("dripScheduleAllBtn").classList.add("hidden");
        const stitchBtn = document.getElementById("stitchCompilationBtn");
        if (stitchBtn) stitchBtn.classList.add("hidden");
        grid.innerHTML = "";
        return;
    }

    clips.forEach(c => {
        currentClipsMap[c.clip_id] = c;
    });

    emptyPlaceholder.classList.add("hidden");
    countBadge.innerText = `${clips.length} Viral Shorts Ready`;
    countBadge.classList.remove("hidden");
    document.getElementById("dripScheduleAllBtn").classList.remove("hidden");
    
    const stitchBtn = document.getElementById("stitchCompilationBtn");
    if (stitchBtn) {
        if (clips.length >= 2) {
            stitchBtn.classList.remove("hidden");
        } else {
            stitchBtn.classList.add("hidden");
        }
    }
    grid.innerHTML = "";

    clips.forEach(clip => {
        const card = document.createElement("div");
        card.className = "glass-panel p-4 shadow-xl space-y-4 border-white/10 flex flex-col";

        const badgeHtml = clip.is_compilation
            ? `<span class="text-xs px-2.5 py-1 rounded-md bg-gradient-to-r from-yellow-500/30 to-amber-500/30 text-yellow-300 font-extrabold border border-yellow-500/50 flex items-center gap-1">
                 <i data-lucide="trophy" class="w-3.5 h-3.5 text-yellow-400"></i> TOP COMPILATION SHORT
               </span>`
            : `<span class="text-xs px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
                 #${clip.rank} Viral Highlight
               </span>`;

        const pinnedCommentHtml = clip.pinned_comment ? `
            <div class="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 space-y-1">
                <div class="flex items-center justify-between text-[10px]">
                    <span class="font-bold text-indigo-300 flex items-center gap-1">
                        <i data-lucide="pin" class="w-3 h-3 text-indigo-400"></i> Viral Pinned Comment (Algorithm Boost):
                    </span>
                    <button onclick="copyClipField('${clip.clip_id}', 'pinned_comment')" class="px-1.5 py-0.5 rounded bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-200 border border-indigo-500/30 transition flex items-center gap-1 text-[9px]">
                        <i data-lucide="copy" class="w-2.5 h-2.5"></i> Copy
                    </button>
                </div>
                <p class="text-[10px] text-gray-300 italic line-clamp-2">${escapeHtml(clip.pinned_comment)}</p>
            </div>
        ` : '';

        const soundBadge = clip.recommended_sound ? `
            <div class="flex items-center justify-between text-[10px] text-gray-400 bg-black/30 px-2 py-1 rounded-lg border border-white/5">
                <span class="flex items-center gap-1"><i data-lucide="music" class="w-3 h-3 text-pink-400"></i> Audio: ${escapeHtml(clip.recommended_sound)}</span>
                <span class="text-amber-400 font-mono text-[9px]">🔥 Peak: 7:30 PM</span>
            </div>
        ` : '';

        card.innerHTML = `
            <!-- Top Badges -->
            <div class="flex items-center justify-between">
                ${badgeHtml}
                <div class="flex items-center gap-1.5">
                    <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold badge-hype">
                        🔥 ${clip.virality_score}% Virality
                    </span>
                    <span class="text-[10px] text-gray-400 font-mono">${clip.duration}s</span>
                </div>
            </div>

            <!-- Video Player (9:16 Vertical with Seamless Loop) -->
            <div class="relative rounded-xl overflow-hidden bg-black aspect-short max-h-[480px] mx-auto border border-white/10">
                <video id="video_${clip.clip_id}" controls loop playsinline preload="metadata" poster="${clip.thumbnail_url}" class="w-full h-full object-cover">
                    <source src="${clip.video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>

            <!-- Title & Hook Snippet with Click-to-Edit -->
            <div class="space-y-1.5">
                <div class="flex items-start justify-between gap-2">
                    <h4 id="title_text_${clip.clip_id}" class="text-xs font-bold text-white leading-snug line-clamp-2 cursor-pointer hover:text-yellow-300 transition" onclick="openEditMetadataModal('${clip.clip_id}')" title="Click to edit title & description">
                        ${escapeHtml(clip.title)}
                    </h4>
                    <button onclick="openEditMetadataModal('${clip.clip_id}')" class="p-1 rounded-lg bg-yellow-500/10 hover:bg-yellow-500/25 border border-yellow-500/30 text-yellow-400 transition flex-shrink-0" title="Edit Title, Tags & Comments">
                        <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
                <p class="text-[10px] text-gray-400 italic line-clamp-2">"${escapeHtml(clip.transcript)}"</p>
                ${soundBadge}
                ${pinnedCommentHtml}
            </div>

            <!-- Action Buttons Grid -->
            <div class="grid grid-cols-2 gap-2 mt-auto pt-2 border-t border-white/5">
                <button onclick="openEditMetadataModal('${clip.clip_id}')" class="py-2 px-2 bg-yellow-500/15 hover:bg-yellow-500/30 border border-yellow-500/40 rounded-lg text-[11px] font-bold text-yellow-300 flex items-center justify-center gap-1.5 transition shadow-sm">
                    <i data-lucide="sparkles" class="w-3.5 h-3.5 text-yellow-400"></i> Edit Viral Metadata
                </button>
                <button onclick="copyClipField('${clip.clip_id}', 'viral_package')" class="py-2 px-2 bg-indigo-600/20 hover:bg-indigo-600/35 border border-indigo-500/30 rounded-lg text-[11px] font-bold text-indigo-200 flex items-center justify-center gap-1.5 transition shadow-sm">
                    <i data-lucide="clipboard-copy" class="w-3.5 h-3.5 text-indigo-400"></i> Copy Viral Bundle
                </button>
                <button onclick="copyClipField('${clip.clip_id}', 'title')" class="py-1.5 px-2 bg-white/5 hover:bg-white/10 rounded-lg text-[11px] font-medium text-gray-300 flex items-center justify-center gap-1.5 transition">
                    <i data-lucide="copy" class="w-3.5 h-3.5 text-indigo-400"></i> Copy Title
                </button>
                <button onclick="copyClipField('${clip.clip_id}', 'tags')" class="py-1.5 px-2 bg-white/5 hover:bg-white/10 rounded-lg text-[11px] font-medium text-gray-300 flex items-center justify-center gap-1.5 transition">
                    <i data-lucide="hash" class="w-3.5 h-3.5 text-pink-400"></i> Copy Tags
                </button>
                <button onclick="copyClipField('${clip.clip_id}', 'pinned_comment')" class="py-1.5 px-2 bg-white/5 hover:bg-white/10 rounded-lg text-[11px] font-medium text-gray-300 flex items-center justify-center gap-1.5 transition">
                    <i data-lucide="pin" class="w-3.5 h-3.5 text-yellow-400"></i> Copy Comment
                </button>
                <button onclick="copyClipField('${clip.clip_id}', 'description')" class="py-1.5 px-2 bg-white/5 hover:bg-white/10 rounded-lg text-[11px] font-medium text-gray-300 flex items-center justify-center gap-1.5 transition">
                    <i data-lucide="file-text" class="w-3.5 h-3.5 text-emerald-400"></i> Copy Description
                </button>
                <button onclick="openVoiceModal('${clip.clip_id}')" class="py-2 px-2 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 rounded-lg text-[11px] font-bold text-purple-200 flex items-center justify-center gap-1.5 transition">
                    <i data-lucide="mic" class="w-3.5 h-3.5 text-purple-300"></i> Add Voiceover
                </button>
                <a href="${clip.video_url}" download="Short_${clip.clip_id}.mp4" class="py-2 px-2 bg-white/10 hover:bg-white/20 rounded-lg text-[11px] font-bold text-white flex items-center justify-center gap-1.5 transition text-center">
                    <i data-lucide="download" class="w-3.5 h-3.5"></i> Download MP4
                </a>
                <button onclick="openPublishModal('${clip.clip_id}')" class="py-2 px-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 rounded-lg text-[11px] font-bold text-white flex items-center justify-center gap-1.5 transition col-span-2 shadow-lg shadow-red-500/20">
                    <i data-lucide="youtube" class="w-4 h-4"></i> Upload / Schedule to YouTube
                </button>
            </div>
        `;

        grid.appendChild(card);
    });

    lucide.createIcons();
}

function openEditMetadataModal(clipId) {
    const clip = currentClipsMap[clipId];
    if (!clip) return;
    activeEditClipId = clipId;

    document.getElementById("editTitleInput").value = clip.title || "";
    document.getElementById("editTitleCharCount").innerText = `${(clip.title || "").length}/100`;
    document.getElementById("editDescTextarea").value = clip.description || "";
    document.getElementById("editTagsInput").value = clip.tags_string || (clip.tags || []).join(" ");
    
    const pinnedCommentInput = document.getElementById("editPinnedCommentInput");
    if (pinnedCommentInput) {
        pinnedCommentInput.value = clip.pinned_comment || "";
    }
    
    // Populate AI Title Suggestions
    const suggestionsList = document.getElementById("editTitleSuggestionsList");
    suggestionsList.innerHTML = "";
    const suggestions = clip.title_suggestions || [];
    if (suggestions.length > 0) {
        document.getElementById("editTitleSuggestionsBox").classList.remove("hidden");
        suggestions.forEach(s => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "text-left text-[11px] p-2 px-3 rounded-lg bg-white/5 hover:bg-yellow-500/20 border border-white/10 text-gray-300 hover:text-yellow-300 transition flex items-center justify-between";
            btn.innerHTML = `<span class="truncate font-medium">${escapeHtml(s)}</span> <i data-lucide="arrow-up-left" class="w-3 h-3 flex-shrink-0 text-yellow-400"></i>`;
            btn.onclick = () => {
                document.getElementById("editTitleInput").value = s;
                document.getElementById("editTitleCharCount").innerText = `${s.length}/100`;
            };
            suggestionsList.appendChild(btn);
        });
        lucide.createIcons();
    } else {
        document.getElementById("editTitleSuggestionsBox").classList.add("hidden");
    }

    document.getElementById("editMetadataModal").classList.remove("hidden");
}

function closeEditMetadataModal() {
    document.getElementById("editMetadataModal").classList.add("hidden");
    activeEditClipId = null;
}

async function saveEditedMetadata() {
    if (!activeEditClipId) return;
    const clip = currentClipsMap[activeEditClipId];
    if (!clip) return;

    const newTitle = document.getElementById("editTitleInput").value.trim() || clip.title;
    const newDesc = document.getElementById("editDescTextarea").value.trim() || clip.description;
    const newTagsStr = document.getElementById("editTagsInput").value.trim();
    const newPinnedComment = document.getElementById("editPinnedCommentInput")?.value.trim() || clip.pinned_comment || "";

    // Update locally in memory
    clip.title = newTitle;
    clip.description = newDesc;
    clip.tags_string = newTagsStr;
    clip.tags = newTagsStr.split(/\s+/).filter(t => t.startsWith("#"));
    clip.pinned_comment = newPinnedComment;
    clip.full_viral_package = `📌 TITLE:\n${newTitle}\n\n💬 PINNED COMMENT:\n${newPinnedComment}\n\n🎬 DESCRIPTION:\n${newDesc}\n\n🔥 HASHTAGS:\n${newTagsStr}`;

    // Update DOM on card
    const titleEl = document.getElementById(`title_text_${activeEditClipId}`);
    if (titleEl) {
        titleEl.innerText = newTitle;
    }

    // Persist to backend
    try {
        await fetch("/api/clips/update-metadata", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                job_id: currentJobId,
                clip_id: activeEditClipId,
                title: newTitle,
                description: newDesc,
                tags: clip.tags,
                pinned_comment: newPinnedComment
            })
        });
    } catch (e) {
        console.error("Update metadata error:", e);
    }

    showToast("Viral Metadata Saved!");
    closeEditMetadataModal();
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function copyClipField(clipId, field) {
    const clip = currentClipsMap[clipId];
    if (!clip) return;

    let text = "";
    let msg = "";
    if (field === "title") {
        text = clip.title;
        msg = "Title Copied!";
    } else if (field === "tags") {
        text = clip.tags_string || (clip.tags || []).join(" ");
        msg = "Trending Hashtags Copied!";
    } else if (field === "description") {
        text = clip.description;
        msg = "Description & Credits Copied!";
    } else if (field === "pinned_comment") {
        text = clip.pinned_comment || "";
        msg = "Algorithm Pinned Comment Copied!";
    } else if (field === "viral_package") {
        text = clip.full_viral_package || `📌 TITLE:\n${clip.title}\n\n💬 PINNED COMMENT:\n${clip.pinned_comment || ''}\n\n🎬 DESCRIPTION:\n${clip.description}\n\n🔥 TRENDING HASHTAGS:\n${clip.tags_string || (clip.tags || []).join(' ')}`;
        msg = "Full Viral Growth Bundle Copied!";
    }

    navigator.clipboard.writeText(text).then(() => {
        showToast(msg);
    }).catch(err => {
        console.error("Clipboard copy failed:", err);
    });
}

// ==================== YOUTUBE SINGLE UPLOAD & TIMERS ====================

async function checkYouTubeStatus() {
    try {
        const res = await fetch("/api/youtube/status");
        const data = await res.json();
        if (data.authenticated) {
            connectedChannelData = data;
            const channelName = data.title || "YouTube Connected";
            document.getElementById("ytChannelName").innerText = channelName;
            document.getElementById("ytConnectedTitle").innerText = channelName;
            document.getElementById("ytPublishModalChannelName").innerText = `Target Channel: ${channelName}`;
            document.getElementById("ytConnectedSubs").innerText = `${data.subscribers || '0'} Subscribers • ${data.video_count || '0'} Videos`;
            if (data.avatar) {
                document.getElementById("ytChannelAvatar").src = data.avatar;
            }
            document.getElementById("ytStatusConnected").classList.remove("hidden");
            document.getElementById("ytSetupSection").classList.add("hidden");
        }
    } catch (e) {
        console.log("YouTube status check:", e);
    }
}

async function setupYouTubeAuth() {
    const clientId = document.getElementById("ytClientIdInput").value.trim();
    const clientSecret = document.getElementById("ytClientSecretInput").value.trim();

    if (!clientId || !clientSecret) {
        alert("Please enter both Client ID and Client Secret from Google Cloud Console!");
        return;
    }

    try {
        const saveRes = await fetch("/api/youtube/setup-credentials", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ client_id: clientId, client_secret: clientSecret })
        });
        if (!saveRes.ok) throw new Error("Could not save credentials");

        const authRes = await fetch("/api/youtube/auth-url");
        const authData = await authRes.json();

        if (authData.auth_url) {
            window.location.href = authData.auth_url;
        } else {
            alert("Failed to get Google OAuth URL");
        }
    } catch (e) {
        alert(`Setup error: ${e.message}`);
    }
}

function openPublishModal(clipId) {
    const clip = currentClipsMap[clipId];
    if (!clip) {
        alert("Clip data not found.");
        return;
    }

    activePublishClipId = clipId;

    // Reset View Sections
    document.getElementById("ytPublishFormSection").classList.remove("hidden");
    document.getElementById("ytPublishLoadingSection").classList.add("hidden");
    document.getElementById("ytPublishSuccessSection").classList.add("hidden");

    // Populate Clip Info
    document.getElementById("publishModalThumb").src = clip.thumbnail_url || '';
    document.getElementById("publishModalRank").innerText = `#${clip.rank} Viral Highlight`;
    document.getElementById("publishModalPreviewTitle").innerText = clip.title;
    document.getElementById("publishModalMeta").innerText = `Duration: ${clip.duration}s • Virality: ${clip.virality_score}%`;

    // Populate Fields
    document.getElementById("publishTitleInput").value = clip.title;
    document.getElementById("publishTitleCharCount").innerText = `${clip.title.length}/100`;
    document.getElementById("publishDescTextarea").value = clip.description;

    // Reset Timing Mode to 'now'
    const nowRadio = document.querySelector('input[name="publishTimingMode"][value="now"]');
    if (nowRadio) nowRadio.checked = true;
    onTimingModeChanged();

    // Set Default Custom Date to Tomorrow 11:00 AM
    setDefaultCustomDatetime();

    document.getElementById("ytPublishModal").classList.remove("hidden");
    lucide.createIcons();
}

function closePublishModal() {
    document.getElementById("ytPublishModal").classList.add("hidden");
    activePublishClipId = null;
}

function getNextPeakViralTime() {
    const now = new Date();
    // 10 Peak YouTube Shorts Viral Slots (Local Browser Time):
    // 7:30 AM, 9:00 AM, 11:30 AM, 1:00 PM, 3:30 PM, 5:00 PM, 7:30 PM, 9:00 PM, 10:30 PM, 12:00 AM (midnight)
    const peakHours = [
        { h: 7, m: 30 },
        { h: 9, m: 0 },
        { h: 11, m: 30 },
        { h: 13, m: 0 },
        { h: 15, m: 30 },
        { h: 17, m: 0 },
        { h: 19, m: 30 },
        { h: 21, m: 0 },
        { h: 22, m: 30 },
        { h: 0, m: 0 }
    ];

    for (const slot of peakHours) {
        let candidate;
        if (slot.h === 0 && slot.m === 0) {
            // Midnight at the end of today / start of tomorrow
            candidate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0, 0);
        } else {
            candidate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), slot.h, slot.m, 0, 0);
        }
        
        // If at least 20 minutes in the future
        if (candidate.getTime() - now.getTime() > 20 * 60 * 1000) {
            return candidate;
        }
    }

    // Otherwise tomorrow morning at 7:30 AM
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 7, 30, 0, 0);
    return tomorrow;
}

function onTimingModeChanged() {
    const mode = document.querySelector('input[name="publishTimingMode"]:checked')?.value || "now";
    const autoBox = document.getElementById("autoTimerInfoBox");
    const manualBox = document.getElementById("customSchedulePickerBox");
    const privacyBox = document.getElementById("publishPrivacyContainer");
    const submitBtnSpan = document.querySelector("#confirmPublishBtn span");

    if (mode === "auto_timer") {
        autoBox.classList.remove("hidden");
        manualBox.classList.add("hidden");
        privacyBox.classList.add("hidden");
        const nextTime = getNextPeakViralTime();
        document.getElementById("autoScheduledTimeBadge").innerText = nextTime.toLocaleString([], {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        submitBtnSpan.innerText = "Schedule with Automatic Smart Timer";
    } else if (mode === "manual_timer") {
        autoBox.classList.add("hidden");
        manualBox.classList.remove("hidden");
        privacyBox.classList.add("hidden");
        submitBtnSpan.innerText = "Schedule with Manual Timer";
    } else {
        autoBox.classList.add("hidden");
        manualBox.classList.add("hidden");
        privacyBox.classList.remove("hidden");
        submitBtnSpan.innerText = "Confirm & Upload to YouTube (Live Now)";
    }
}

function formatDatetimeForInput(dt) {
    const year = dt.getFullYear();
    const month = String(dt.getMonth() + 1).padStart(2, '0');
    const day = String(dt.getDate()).padStart(2, '0');
    const hours = String(dt.getHours()).padStart(2, '0');
    const mins = String(dt.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${mins}`;
}

function setDefaultCustomDatetime() {
    const nextSlot = getNextPeakViralTime();
    document.getElementById("customPublishDatetime").value = formatDatetimeForInput(nextSlot);
}

function applySchedulePreset(pill) {
    const hoursOffset = pill.getAttribute("data-hours");
    const slot = pill.getAttribute("data-slot");
    const preset = pill.getAttribute("data-preset");
    const now = new Date();

    if (hoursOffset) {
        now.setHours(now.getHours() + parseInt(hoursOffset, 10));
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(now);
        return;
    }

    if (slot) {
        const h = parseInt(slot.substring(0, 2), 10);
        const m = parseInt(slot.substring(2, 4), 10);
        let targetDate;
        if (h === 0 && m === 0) {
            targetDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0, 0);
        } else {
            targetDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, 0, 0);
            // If slot already passed today or within 20 mins, schedule for tomorrow at this time
            if (targetDate.getTime() - now.getTime() <= 20 * 60 * 1000) {
                targetDate.setDate(targetDate.getDate() + 1);
            }
        }
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(targetDate);
        return;
    }

    if (preset === "tomorrow_1100") {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        d.setHours(11, 0, 0, 0);
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(d);
    } else if (preset === "tomorrow_1530") {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        d.setHours(15, 30, 0, 0);
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(d);
    } else if (preset === "tomorrow_1930") {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        d.setHours(19, 30, 0, 0);
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(d);
    } else if (preset === "nextday_1100") {
        const d = new Date();
        d.setDate(d.getDate() + 2);
        d.setHours(11, 0, 0, 0);
        document.getElementById("customPublishDatetime").value = formatDatetimeForInput(d);
    }
}

async function submitPublishShort() {
    if (!activePublishClipId) return;

    const clip = currentClipsMap[activePublishClipId];
    if (!clip) return;

    const title = document.getElementById("publishTitleInput").value.trim();
    const description = document.getElementById("publishDescTextarea").value.trim();
    const timingMode = document.querySelector('input[name="publishTimingMode"]:checked')?.value || "now";
    const privacy = document.getElementById("publishPrivacySelect").value;

    if (!title) {
        alert("Please enter a title for the Short!");
        return;
    }

    let publishAtIso = null;
    let publishFormattedTime = "";

    if (timingMode === "auto_timer") {
        const autoDate = getNextPeakViralTime();
        publishAtIso = autoDate.toISOString();
        publishFormattedTime = autoDate.toLocaleString([], {
            dateStyle: "medium",
            timeStyle: "short"
        });
    } else if (timingMode === "manual_timer") {
        const dtVal = document.getElementById("customPublishDatetime").value;
        if (!dtVal) {
            alert("Please pick a date and time to schedule!");
            return;
        }

        const scheduledDate = new Date(dtVal);
        const now = new Date();
        if (scheduledDate <= now) {
            alert("The scheduled date and time must be in the future!");
            return;
        }

        publishAtIso = scheduledDate.toISOString();
        publishFormattedTime = scheduledDate.toLocaleString([], {
            dateStyle: "medium",
            timeStyle: "short"
        });
    }

    // Switch to loading UI
    document.getElementById("ytPublishFormSection").classList.add("hidden");
    document.getElementById("ytPublishLoadingSection").classList.remove("hidden");

    try {
        const res = await fetch("/api/youtube/upload-short", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                clip_id: activePublishClipId,
                title: title,
                description: description,
                tags: clip.tags || ["#Shorts"],
                privacy: (timingMode === "auto_timer" || timingMode === "manual_timer") ? "private" : privacy,
                publish_at: publishAtIso
            })
        });

        const data = await res.json();

        if (res.ok) {
            document.getElementById("ytPublishLoadingSection").classList.add("hidden");
            document.getElementById("ytPublishSuccessSection").classList.remove("hidden");

            if (timingMode !== "now") {
                document.getElementById("ytPublishSuccessMsg").innerHTML = `
                    Your Short was uploaded and <strong class="text-indigo-400 font-bold">scheduled to go public</strong> on:<br>
                    <span class="text-sm font-semibold text-white mt-1 inline-block">📅 ${publishFormattedTime}</span>
                `;
            } else {
                document.getElementById("ytPublishSuccessMsg").innerText = "Your Short is now live on your YouTube channel!";
            }

            document.getElementById("ytPublishOpenUrlBtn").href = data.youtube_url || `https://youtube.com/shorts/${data.video_id}`;
            showToast(timingMode !== "now" ? "Short successfully scheduled on YouTube!" : "Short successfully published to YouTube!");
            lucide.createIcons();
        } else {
            alert(`YouTube upload error: ${data.detail || 'Upload failed'}`);
            document.getElementById("ytPublishLoadingSection").classList.add("hidden");
            document.getElementById("ytPublishFormSection").classList.remove("hidden");
        }
    } catch (e) {
        console.error(e);
        alert("Failed to communicate with YouTube API backend.");
        document.getElementById("ytPublishLoadingSection").classList.add("hidden");
        document.getElementById("ytPublishFormSection").classList.remove("hidden");
    }
}

// ==================== YOUTUBE BATCH SCHEDULER ====================

function openBatchScheduleModal() {
    const clips = Object.values(currentClipsMap);
    if (clips.length === 0) {
        alert("No clips available to schedule!");
        return;
    }

    // Reset views
    document.getElementById("ytBatchFormSection").classList.remove("hidden");
    document.getElementById("ytBatchLoadingSection").classList.add("hidden");
    document.getElementById("ytBatchResultsSection").classList.add("hidden");

    // Default to auto
    const autoRadio = document.querySelector('input[name="batchMode"][value="auto"]');
    if (autoRadio) autoRadio.checked = true;

    // Set default start time to Tomorrow 11:00 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(11, 0, 0, 0);
    document.getElementById("batchStartDatetime").value = formatDatetimeForInput(tomorrow);

    updateBatchSchedulePreview();

    document.getElementById("ytBatchScheduleModal").classList.remove("hidden");
    lucide.createIcons();
}

function closeBatchScheduleModal() {
    document.getElementById("ytBatchScheduleModal").classList.add("hidden");
}

function onBatchModeChanged() {
    const mode = document.querySelector('input[name="batchMode"]:checked')?.value || "auto";
    const cadenceSelect = document.getElementById("batchCadenceSelect");

    if (mode === "auto") {
        cadenceSelect.value = "3_peak";
    } else {
        cadenceSelect.value = "every_6h";
    }
    updateBatchSchedulePreview();
}

function updateBatchSchedulePreview() {
    const clips = Object.values(currentClipsMap);
    const container = document.getElementById("batchSchedulePreviewList");
    if (!container || clips.length === 0) return;

    const startVal = document.getElementById("batchStartDatetime").value;
    const baseDate = startVal ? new Date(startVal) : new Date();
    const cadence = document.getElementById("batchCadenceSelect").value;

    container.innerHTML = "";

    const previewTimes = calculateBatchTimes(clips.length, baseDate, cadence);

    clips.forEach((clip, idx) => {
        const t = previewTimes[idx];
        const timeFormatted = t.toLocaleString([], {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const row = document.createElement("div");
        row.className = "flex items-center justify-between p-2 rounded-lg bg-white/5 text-[11px] border border-white/5";
        row.innerHTML = `
            <div class="flex items-center gap-2 truncate pr-2">
                <span class="font-bold text-indigo-400">#${clip.rank}</span>
                <span class="text-white truncate">${escapeHtml(clip.title)}</span>
            </div>
            <span class="text-emerald-400 font-mono flex-shrink-0 text-[10px]">📅 ${timeFormatted}</span>
        `;
        container.appendChild(row);
    });
}

function calculateBatchTimes(numClips, baseDate, cadence) {
    const times = [];
    let current = new Date(baseDate.getTime());

    if (cadence === "every_4h") {
        for (let i = 0; i < numClips; i++) {
            const dt = new Date(current.getTime() + (i * 4 * 3600 * 1000));
            times.push(dt);
        }
    } else if (cadence === "every_6h") {
        for (let i = 0; i < numClips; i++) {
            const dt = new Date(current.getTime() + (i * 6 * 3600 * 1000));
            times.push(dt);
        }
    } else if (cadence === "every_12h") {
        for (let i = 0; i < numClips; i++) {
            const dt = new Date(current.getTime() + (i * 12 * 3600 * 1000));
            times.push(dt);
        }
    } else if (cadence === "every_24h") {
        for (let i = 0; i < numClips; i++) {
            const dt = new Date(current.getTime() + (i * 24 * 3600 * 1000));
            times.push(dt);
        }
    } else {
        // Peak hours options
        let peakSlots = [
            { h: 11, m: 0 },
            { h: 15, m: 30 },
            { h: 19, m: 30 }
        ];

        if (cadence === "2_peak") {
            peakSlots = [
                { h: 11, m: 0 },
                { h: 19, m: 30 }
            ];
        } else if (cadence === "1_peak") {
            peakSlots = [
                { h: 19, m: 30 }
            ];
        }

        let dayOffset = 0;
        let slotIdx = 0;

        for (let i = 0; i < numClips; i++) {
            const slot = peakSlots[slotIdx % peakSlots.length];
            const dt = new Date(baseDate.getFullYear(), baseDate.getMonth(), baseDate.getDate() + dayOffset, slot.h, slot.m, 0, 0);

            times.push(dt);
            slotIdx++;
            if (slotIdx % peakSlots.length === 0) {
                dayOffset++;
            }
        }
    }

    return times;
}

async function submitBatchSchedule() {
    if (!currentJobId) {
        alert("No active job to schedule!");
        return;
    }

    const startVal = document.getElementById("batchStartDatetime").value;
    const cadence = document.getElementById("batchCadenceSelect").value;
    const startIso = startVal ? new Date(startVal).toISOString() : new Date().toISOString();

    let shortsPerDay = 3;
    let customHours = [11, 15.5, 19.5];
    let intervalHours = null;

    if (cadence === "2_peak") {
        shortsPerDay = 2;
        customHours = [11, 19.5];
    } else if (cadence === "1_peak") {
        shortsPerDay = 1;
        customHours = [19.5];
    } else if (cadence === "every_4h") {
        intervalHours = 4;
    } else if (cadence === "every_6h") {
        intervalHours = 6;
    } else if (cadence === "every_12h") {
        intervalHours = 12;
    } else if (cadence === "every_24h") {
        intervalHours = 24;
    }

    // Switch to Loading View
    document.getElementById("ytBatchFormSection").classList.add("hidden");
    document.getElementById("ytBatchLoadingSection").classList.remove("hidden");

    try {
        const res = await fetch("/api/youtube/drip-schedule-all", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                job_id: currentJobId,
                start_datetime: startIso,
                shorts_per_day: shortsPerDay,
                custom_hours: customHours,
                interval_hours: intervalHours
            })
        });

        const data = await res.json();

        if (res.ok) {
            document.getElementById("ytBatchLoadingSection").classList.add("hidden");
            document.getElementById("ytBatchResultsSection").classList.remove("hidden");
            document.getElementById("batchResultsSummary").innerText = `Successfully scheduled ${data.total_scheduled} Shorts on YouTube!`;

            const resultsList = document.getElementById("batchResultsList");
            resultsList.innerHTML = "";

            (data.results || []).forEach(r => {
                const item = document.createElement("div");
                item.className = "flex items-center justify-between p-2 rounded-lg bg-white/5 border border-white/5 text-[11px]";
                if (r.status === "scheduled") {
                    item.innerHTML = `
                        <span class="text-white truncate">📅 ${r.scheduled_for}</span>
                        <a href="${r.youtube_url}" target="_blank" class="px-2 py-1 bg-red-600 hover:bg-red-500 rounded text-[10px] text-white font-bold transition flex items-center gap-1">
                            <i data-lucide="external-link" class="w-3 h-3"></i> View
                        </a>
                    `;
                } else {
                    item.innerHTML = `
                        <span class="text-red-400 truncate">Failed: ${r.error || 'Unknown'}</span>
                    `;
                }
                resultsList.appendChild(item);
            });

            showToast(`Batch scheduled ${data.total_scheduled} Shorts on YouTube!`);
            lucide.createIcons();
        } else {
            alert(`Batch schedule error: ${data.detail || 'Failed to schedule'}`);
            document.getElementById("ytBatchLoadingSection").classList.add("hidden");
            document.getElementById("ytBatchFormSection").classList.remove("hidden");
        }
    } catch (e) {
        console.error(e);
        alert("Failed to communicate with YouTube API backend.");
        document.getElementById("ytBatchLoadingSection").classList.add("hidden");
        document.getElementById("ytBatchFormSection").classList.remove("hidden");
    }
}

function showToast(msg) {
    const toast = document.createElement("div");
    toast.className = "fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-2xl transition transform translate-y-4 opacity-0 flex items-center gap-2";
    toast.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4"></i> ${msg}`;
    document.body.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.classList.remove("translate-y-4", "opacity-0");
    }, 50);

    setTimeout(() => {
        toast.classList.add("translate-y-4", "opacity-0");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== VOICEOVER STUDIO ====================

function openVoiceModal(clipId) {
    activeVoiceClipId = clipId;
    const clip = currentClipsMap[clipId];
    
    // Auto populate smart hook if empty
    const textArea = document.getElementById("ttsCommentaryText");
    if (clip && (!textArea.value || textArea.value.trim().length === 0)) {
        textArea.value = `Wait until you see what happens at the end of this crazy ${clip.creator_name || 'stream'} moment!`;
    }

    document.getElementById("voiceModal").classList.remove("hidden");
    recordedBlob = null;
    document.getElementById("applyMicBtn").disabled = true;
    document.getElementById("recordedAudioPreview").classList.add("hidden");
    document.getElementById("voicePreviewAudio").classList.add("hidden");
    document.getElementById("voiceWaveAnimation").classList.add("hidden");
}

async function previewTtsVoiceover() {
    const text = document.getElementById("ttsCommentaryText").value.trim() || "Wait until you see what happens next in this crazy clip!";
    const voice = document.getElementById("ttsVoiceSelect").value;
    const btn = document.getElementById("previewVoiceBtn");
    const audioEl = document.getElementById("voicePreviewAudio");
    const waveEl = document.getElementById("voiceWaveAnimation");

    btn.disabled = true;
    btn.innerHTML = `<div class="w-3 h-3 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div> Synthesizing...`;

    try {
        const res = await fetch("/api/preview-voice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, voice_type: voice })
        });
        const data = await res.json();
        if (res.ok && data.audio_url) {
            audioEl.src = `${data.audio_url}?t=${Date.now()}`;
            audioEl.classList.remove("hidden");
            waveEl.classList.remove("hidden");
            audioEl.play();
            audioEl.onended = () => {
                waveEl.classList.add("hidden");
            };
            showToast("Playing Studio Mastered Voice Preview!");
        } else {
            showToast("Could not preview voice");
        }
    } catch (e) {
        console.error("Preview voice error:", e);
        showToast("Error synthesizing voice preview");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="volume-2" class="w-3.5 h-3.5 text-purple-400"></i> <span>Preview Audio</span>`;
        lucide.createIcons();
    }
}

async function toggleMicRecording() {
    const btn = document.getElementById("recordMicBtn");
    const btnText = document.getElementById("recordMicBtnText");

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        btnText.innerText = "Start Recording";
        btn.classList.remove("bg-rose-600", "text-white");
    } else {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                recordedBlob = new Blob(audioChunks, { type: "audio/wav" });
                const audioUrl = URL.createObjectURL(recordedBlob);
                const preview = document.getElementById("recordedAudioPreview");
                preview.src = audioUrl;
                preview.classList.remove("hidden");
                document.getElementById("applyMicBtn").disabled = false;
            };

            mediaRecorder.start();
            btnText.innerText = "Stop Recording...";
            btn.classList.add("bg-rose-600", "text-white");
        } catch (err) {
            alert("Microphone permission denied or not available.");
        }
    }
}

async function submitMicVoiceover() {
    if (!recordedBlob || !activeVoiceClipId) return;

    const btn = document.getElementById("applyMicBtn");
    btn.disabled = true;
    btn.innerText = "Mixing Voiceover into Short...";

    const formData = new FormData();
    formData.append("clip_id", activeVoiceClipId);
    formData.append("audio_file", recordedBlob, "mic_voice.wav");

    try {
        const res = await fetch("/api/add-voiceover", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("voiceModal").classList.add("hidden");
            showToast("Voiceover mixed successfully!");
            const vid = document.getElementById(`video_${activeVoiceClipId}`);
            if (vid) {
                vid.src = `${data.dubbed_video_url}?t=${Date.now()}`;
                vid.load();
                vid.play();
            }
        } else {
            alert(`Voiceover error: ${data.detail}`);
        }
    } catch (e) {
        console.error(e);
        alert("Failed to submit voiceover audio.");
    } finally {
        btn.disabled = false;
        btn.innerText = "Apply Recorded Voiceover to Short";
    }
}

async function submitTtsVoiceover() {
    const text = document.getElementById("ttsCommentaryText").value.trim();
    const voice = document.getElementById("ttsVoiceSelect").value;
    if (!text || !activeVoiceClipId) {
        alert("Please enter commentary text!");
        return;
    }

    const btn = document.getElementById("applyTtsBtn");
    btn.disabled = true;
    btn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div> Mastering & Mixing Audio...`;

    const formData = new FormData();
    formData.append("clip_id", activeVoiceClipId);
    formData.append("voiceover_text", text);
    formData.append("voice_type", voice);

    try {
        const res = await fetch("/api/add-voiceover", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("voiceModal").classList.add("hidden");
            showToast("Studio AI Voiceover added with High-Punch Audio!");
            const vid = document.getElementById(`video_${activeVoiceClipId}`);
            if (vid) {
                vid.src = `${data.dubbed_video_url}?t=${Date.now()}`;
                vid.load();
                vid.play();
            }
        } else {
            alert(`AI Voice error: ${data.detail}`);
        }
    } catch (e) {
        console.error(e);
        alert("Failed to generate AI voiceover.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i> Generate & Mix Voiceover to Short`;
        lucide.createIcons();
    }
}

// ==================== TOAST NOTIFICATION UTILITY ====================

function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 pointer-events-none";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = "pointer-events-auto px-4 py-3 rounded-xl bg-gray-950/95 text-white text-xs font-semibold shadow-2xl border border-indigo-500/40 backdrop-blur-md flex items-center gap-2.5 transform transition-all duration-300 translate-y-4 opacity-0 max-w-sm";
    
    const iconColor = type === "error" ? "text-rose-400" : "text-emerald-400";
    const iconName = type === "error" ? "alert-circle" : "check-circle-2";

    toast.innerHTML = `
        <i data-lucide="${iconName}" class="w-4 h-4 ${iconColor} flex-shrink-0"></i>
        <span class="flex-1 leading-snug">${escapeHtml(message)}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons();

    // Fade in
    requestAnimationFrame(() => {
        toast.classList.remove("translate-y-4", "opacity-0");
        toast.classList.add("translate-y-0", "opacity-100");
    });

    // Auto dismiss
    setTimeout(() => {
        toast.classList.remove("translate-y-0", "opacity-100");
        toast.classList.add("translate-y-2", "opacity-0");
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3500);
}
