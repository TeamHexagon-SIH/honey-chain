const API_HOST = window.location.hostname || "127.0.0.1";
const API_BASE = `http://${API_HOST}:8000/api`;

let currentHiveId = 1;
let currentBatchId = null;


// ============================================================
// BASIC API HELPER
// ============================================================

async function apiFetch(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);

        if (!response.ok) {
            throw new Error(`API error ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        return null;
    }
}


// ============================================================
// BACKEND STATUS
// ============================================================

async function checkBackendStatus() {

    const statusElement =
        document.querySelector("#backendStatus");

    try {

        const response =
            await fetch(`http://${API_HOST}:8000/health`);

        if (response.ok) {

            if (statusElement) {

                statusElement.textContent =
                    "Backend Online";

                statusElement.classList.add("online");
            }

        } else {

            if (statusElement) {
                statusElement.textContent =
                    "Backend Offline";
            }
        }

    } catch (error) {

        if (statusElement) {
            statusElement.textContent =
                "Backend Offline";
        }
    }
}


// ============================================================
// HIVE DATA
// ============================================================

async function loadHiveData() {

    const hive =
        await apiFetch(`/hives/${currentHiveId}`);

    if (!hive) return;

    console.log("Hive:", hive);
}


// ============================================================
// LATEST SENSOR READING
// ============================================================

async function loadSensorData() {

    const data =
        await apiFetch(
            `/sensors/latest/${currentHiveId}`
        );

    if (!data) return;

    console.log(
        "Latest sensor reading:",
        data
    );

    // Dashboard KPI cards
    updateElement(
        "temperature",
        data.temperature,
        " °C"
    );

    updateElement(
        "humidity",
        data.humidity,
        " %"
    );

    updateElement(
        "weight",
        data.hive_weight,
        " kg"
    );

    updateElement(
        "acoustic",
        data.acoustic_level,
        ""
    );


    // Hive Monitoring page
    updateElement(
        "hive-temperature",
        data.temperature,
        " °C"
    );

    updateElement(
        "hive-humidity",
        data.humidity,
        " %"
    );

    updateElement(
        "hive-weight",
        data.hive_weight,
        " kg"
    );

    updateElement(
        "hive-acoustic",
        data.acoustic_level,
        ""
    );
}


// ============================================================
// AI HEALTH
// ============================================================

async function loadHealthData() {

    const sensor =
        await apiFetch(
            `/sensors/latest/${currentHiveId}`
        );

    if (!sensor) return;

    try {

        const params = new URLSearchParams({

            hive_id: currentHiveId,

            temperature:
                sensor.temperature,

            humidity:
                sensor.humidity,

            hive_weight:
                sensor.hive_weight,

            acoustic_level:
                sensor.acoustic_level
        });


        const response =
            await fetch(
                `${API_BASE}/ai/health?${params.toString()}`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Health API failed: ${response.status}`
            );
        }


        const health =
            await response.json();

        console.log(
            "AI Health:",
            health
        );


        // AI Health panel

        updateElement(
            "health-score",
            Math.round(
                health.health_score
            ),
            ""
        );


        updateElement(
            "health-status",
            health.health_status,
            ""
        );


        updateElement(
            "risk",
            health.risk_indicator,
            ""
        );


        // Store result for yield prediction

        window.latestHealthScore =
            health.health_score;


    } catch (error) {

        console.error(
            "AI health error:",
            error
        );
    }
}


// ============================================================
// YIELD PREDICTION
// ============================================================

async function loadYieldPrediction() {

    const sensor =
        await apiFetch(
            `/sensors/latest/${currentHiveId}`
        );

    if (!sensor) return;

    try {

        const healthScore =
            window.latestHealthScore ?? 90;


        // Demo flowering score
        const floweringScore = 0.75;


        const params =
            new URLSearchParams({

                hive_id:
                    currentHiveId,

                temperature:
                    sensor.temperature,

                humidity:
                    sensor.humidity,

                hive_weight:
                    sensor.hive_weight,

                flowering_score:
                    floweringScore,

                health_score:
                    healthScore
            });


        const response =
            await fetch(
                `${API_BASE}/ai/yield?${params.toString()}`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Yield API failed: ${response.status}`
            );
        }


        const result =
            await response.json();


        console.log(
            "Yield prediction:",
            result
        );


        updateElement(
            "predicted-yield",
            Number(
                result.predicted_yield_kg
            ).toFixed(1),
            " kg"
        );


        updateElement(
            "flowering-score",
            floweringScore.toFixed(2),
            ""
        );


    } catch (error) {

        console.error(
            "Yield prediction error:",
            error
        );
    }
}


// ============================================================
// HONEY BATCHES
// ============================================================

async function loadBatches() {

    const batches =
        await apiFetch("/batches/");

    if (!batches) return;

    console.log(
        "Honey batches:",
        batches
    );


    const container =
        document.getElementById(
            "batch-list"
        );


    if (!container) {

        console.warn(
            "Batch list container not found."
        );

        return;
    }


    if (batches.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                <p>No honey batches found.</p>
            </div>
        `;

        return;
    }


    // Latest batch
    const latestBatch =
        batches[batches.length - 1];


    currentBatchId =
        latestBatch.id;


    // Dashboard summary

    updateElement(
        "batch-code",
        latestBatch.batch_code,
        ""
    );


    updateElement(
        "batch-quantity",
        latestBatch.quantity_kg,
        " kg"
    );


    updateElement(
        "batch-status",
        latestBatch.status,
        ""
    );


    // Display all batches

    container.innerHTML =
        batches.map(batch => `

            <div class="batch-card">

                <div class="batch-card-header">

                    <div>

                        <h3>
                            ${batch.batch_code}
                        </h3>

                        <p>
                            Honey Production Batch
                        </p>

                    </div>

                    <span class="batch-status">
                        ${batch.status}
                    </span>

                </div>


                <div class="batch-details">

                    <div>

                        <span>
                            Quantity
                        </span>

                        <strong>
                            ${batch.quantity_kg} kg
                        </strong>

                    </div>


                    <div>

                        <span>
                            Hive ID
                        </span>

                        <strong>
                            HIVE-${String(
                                batch.hive_id
                            ).padStart(2, "0")}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Harvest Date
                        </span>

                        <strong>
                            ${batch.harvest_date || "N/A"}
                        </strong>

                    </div>

                </div>


                <div class="batch-actions">

                    <button
                        onclick="viewBatchTraceability(${batch.id})">
                        View Traceability
                    </button>


                    <button
                        onclick="generateBatchQR(${batch.id})">
                        Generate QR
                    </button>

                </div>

            </div>

        `).join("");
}


// ============================================================
// BATCH TRACEABILITY
// ============================================================

async function viewBatchTraceability(batchId) {

    const result =
        await apiFetch(
            `/batches/${batchId}/history`
        );

    if (!result) return;

    console.log(
        "Traceability history:",
        result
    );


    const container =
        document.getElementById(
            "batch-list"
        );


    if (!container) return;


    const isValid =
        result.chain_verification?.valid ??
        result.verification?.valid ??
        false;


    const events =
        result.events || [];


    const eventIcons = {

        HARVEST: "🍯",

        LAB_TEST: "🧪",

        PACKAGING: "📦",

        DISTRIBUTION: "🚚",

        RETAIL: "🏪"
    };


    const timelineHTML =
        events.map(
            (event, index) => {

                const icon =
                    eventIcons[
                        event.event_type
                    ] || "🔗";


                const previousHash =
                    event.previous_hash || "N/A";


                const currentHash =
                    event.current_hash || "N/A";


                return `

                    <div class="timeline-item">

                        <div class="timeline-marker">
                            ${icon}
                        </div>


                        <div class="timeline-content">

                            <div class="timeline-header">

                                <h3>
                                    ${event.event_type}
                                </h3>

                                <span>
                                    Event #${index + 1}
                                </span>

                            </div>


                            <p class="timeline-location">
                                📍 ${event.location || "N/A"}
                            </p>


                            <p class="timeline-description">
                                ${event.description || ""}
                            </p>


                            <div class="hash-info">

                                <small>

                                    Previous Hash:

                                    <code>
                                        ${previousHash.substring(0, 18)}...
                                    </code>

                                </small>


                                <small>

                                    Current Hash:

                                    <code>
                                        ${currentHash.substring(0, 18)}...
                                    </code>

                                </small>

                            </div>

                        </div>

                    </div>

                `;
            }
        ).join("");


    container.innerHTML = `

        <div class="traceability-container">


            <div class="traceability-header">

                <div>

                    <h2>
                        🔗 Honey Chain Traceability
                    </h2>

                    <p>
                        Batch:
                        <strong>
                            ${result.batch_code || "N/A"}
                        </strong>
                    </p>

                </div>


                <div
                    class="chain-status ${
                        isValid
                            ? "valid"
                            : "invalid"
                    }">

                    ${
                        isValid
                            ? "✓ Chain Verified"
                            : "⚠ Tampering Detected"
                    }

                </div>

            </div>


            <div class="timeline">

                ${
                    timelineHTML ||
                    `
                    <div class="empty-state">
                        <p>
                            No traceability events found.
                        </p>
                    </div>
                    `
                }

            </div>


            <button
                class="back-button"
                onclick="loadBatches()">

                ← Back to Batches

            </button>


        </div>

    `;
}


// ============================================================
// GENERATE QR CODE
// ============================================================

async function generateBatchQR(batchId) {

    try {

        const response =
            await fetch(
                `${API_BASE}/batches/${batchId}/qr`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `QR generation failed: ${response.status} ${errorText}`
            );
        }


        const result =
            await response.json();


        console.log(
            "QR generated:",
            result
        );


        // Remove old popup

        const existingPopup =
            document.getElementById(
                "qr-popup"
            );


        if (existingPopup) {
            existingPopup.remove();
        }


        /*
         * IMPORTANT:
         *
         * Backend returns:
         * /qr/HC26-0001.png
         *
         * We build:
         * http://CURRENT-IP:8000/qr/HC26-0001.png
         *
         * Therefore you do NOT need to
         * manually change the IP.
         */

        const qrImageUrl =
            `http://${window.location.hostname}:8000${result.qr_image_url}`;


        console.log(
            "QR image URL:",
            qrImageUrl
        );


        console.log(
            "Verification URL:",
            result.verification_url
        );


        // Create popup

        const popup =
            document.createElement("div");


        popup.id =
            "qr-popup";


        popup.innerHTML = `

            <div class="qr-overlay">

                <div class="qr-modal">


                    <button
                        class="qr-close"
                        onclick="closeQRPopup()">

                        ×

                    </button>


                    <div class="qr-modal-header">

                        <h2>
                            🍯 Honey Chain QR
                        </h2>

                        <p>
                            Scan to verify this honey batch
                        </p>

                    </div>


                    <div class="qr-image-container">

                        <img
                            src="${qrImageUrl}"
                            alt="Honey Chain QR Code"
                            class="qr-image"
                            onerror="handleQRImageError(this)"
                        >

                    </div>


                    <div class="qr-batch-info">

                        <span>
                            Batch Code
                        </span>

                        <strong>
                            ${result.batch_code}
                        </strong>

                    </div>


                    <p class="qr-instruction">

                        📱 Scan this QR code with a phone
                        to open the consumer verification page.

                    </p>


                    <button
                        class="primary-button"
                        onclick="closeQRPopup()">

                        Close

                    </button>


                </div>

            </div>

        `;


        document.body.appendChild(
            popup
        );


    } catch (error) {

        console.error(
            "QR error:",
            error
        );


        alert(
            `Could not generate QR code.\n\n${error.message}`
        );
    }
}


// ============================================================
// QR IMAGE ERROR HANDLER
// ============================================================

function handleQRImageError(image) {

    console.error(
        "QR image failed to load:",
        image.src
    );


    image.style.display =
        "none";


    const container =
        image.parentElement;


    if (container) {

        container.innerHTML = `

            <div
                style="
                    padding: 30px;
                    text-align: center;
                ">

                <p>
                    ⚠ QR image could not be loaded.
                </p>

                <small>
                    Check that the backend QR file
                    is accessible.
                </small>

            </div>

        `;
    }
}


// ============================================================
// CLOSE QR POPUP
// ============================================================

function closeQRPopup() {

    const popup =
        document.getElementById(
            "qr-popup"
        );


    if (popup) {
        popup.remove();
    }
}


// ============================================================
// TRACEABILITY
// ============================================================

async function loadTraceability() {

    if (!currentBatchId) {
        console.warn(
            "No current batch selected."
        );

        return;
    }


    const history =
        await apiFetch(
            `/batches/${currentBatchId}/history`
        );


    if (!history) return;


    console.log(
        "Traceability:",
        history
    );


    const verification =
        history.chain_verification ||
        history.verification;


    if (verification) {

        console.log(
            "Chain valid:",
            verification.valid
        );
    }
}


// ============================================================
// KVIC / CLUSTER DATA
// ============================================================

async function loadClusters() {

    try {

        const [
            clusters,
            beekeepers,
            hives,
            batches
        ] = await Promise.all([

            apiFetch("/clusters/"),

            apiFetch("/beekeepers/"),

            apiFetch("/hives/"),

            apiFetch("/batches/")
        ]);


        console.log(
            "KVIC Clusters:",
            clusters
        );


        console.log(
            "KVIC Beekeepers:",
            beekeepers
        );


        console.log(
            "KVIC Hives:",
            hives
        );


        console.log(
            "KVIC Batches:",
            batches
        );


        // ====================================================
        // SUMMARY COUNTS
        // ====================================================

        updateElement(
            "cluster-count",
            clusters
                ? clusters.length
                : 0,
            ""
        );


        updateElement(
            "beekeeper-count",
            beekeepers
                ? beekeepers.length
                : 0,
            ""
        );


        updateElement(
            "hive-count",
            hives
                ? hives.length
                : 0,
            ""
        );


        updateElement(
            "batch-count",
            batches
                ? batches.length
                : 0,
            ""
        );


        // ====================================================
        // CLUSTER LIST
        // ====================================================

        const container =
            document.getElementById(
                "cluster-list"
            );


        if (!container) {

            console.warn(
                "Cluster list container not found."
            );

            return;
        }


        if (
            !clusters ||
            clusters.length === 0
        ) {

            container.innerHTML = `

                <div class="empty-state">

                    <p>
                        No clusters found.
                    </p>

                </div>

            `;

            return;
        }


        // ====================================================
        // BUILD CLUSTER CARDS
        // ====================================================

        container.innerHTML =
            clusters.map(
                cluster => {

                    const clusterBeekeepers =
                        beekeepers
                            ? beekeepers.filter(
                                beekeeper =>
                                    beekeeper.cluster_id ===
                                    cluster.id
                            )
                            : [];


                    const clusterBeekeeperIds =
                        clusterBeekeepers.map(
                            beekeeper =>
                                beekeeper.id
                        );


                    const clusterHives =
                        hives
                            ? hives.filter(
                                hive =>
                                    clusterBeekeeperIds.includes(
                                        hive.beekeeper_id
                                    )
                            )
                            : [];


                    return `

                        <div class="cluster-card">


                            <div class="cluster-card-header">

                                <div>

                                    <h3>
                                        ${cluster.name}
                                    </h3>

                                    <p>
                                        ${cluster.district},
                                        ${cluster.state}
                                    </p>

                                </div>


                                <span class="cluster-badge">
                                    ACTIVE
                                </span>

                            </div>


                            <div class="cluster-stats">


                                <div>

                                    <span>
                                        Beekeepers
                                    </span>

                                    <strong>
                                        ${clusterBeekeepers.length}
                                    </strong>

                                </div>


                                <div>

                                    <span>
                                        Hives
                                    </span>

                                    <strong>
                                        ${clusterHives.length}
                                    </strong>

                                </div>


                            </div>


                        </div>

                    `;
                }
            ).join("");


    } catch (error) {

        console.error(
            "KVIC dashboard error:",
            error
        );
    }
}


// ============================================================
// CONSUMER HONEY VERIFICATION
// ============================================================

async function verifyHoney() {

    const input =
        document.getElementById(
            "verify-batch-code"
        );


    const resultContainer =
        document.getElementById(
            "consumer-result"
        );


    if (
        !input ||
        !resultContainer
    ) {

        console.error(
            "Verification elements not found."
        );

        return;
    }


    const batchCode =
        input.value.trim();


    if (!batchCode) {

        resultContainer.innerHTML = `

            <div class="verification-error">

                Please enter a batch code.

            </div>

        `;

        return;
    }


    resultContainer.innerHTML = `

        <div class="verification-loading">

            Verifying batch...

        </div>

    `;


    try {

        const result =
            await apiFetch(
                `/verify/${encodeURIComponent(batchCode)}`
            );


        if (!result) {

            resultContainer.innerHTML = `

                <div class="verification-error">

                    Batch could not be verified.

                </div>

            `;

            return;
        }


        console.log(
            "Verification result:",
            result
        );


        const chainValid =
            result.tamper_check?.valid ??
            false;


        const batch =
            result.batch || {};


        const beekeeper =
            result.beekeeper || {};


        const cluster =
            result.cluster || {};


        const aiHealth =
            result.ai_health || null;


        const labTests =
            result.lab_tests || [];


        const traceability =
            result.traceability || [];


        // ====================================================
        // BUILD VERIFICATION PAGE
        // ====================================================

        resultContainer.innerHTML = `

            <div class="consumer-verification">


                <div class="verification-header">


                    <div>

                        <h2>
                            🍯 Honey Verification
                        </h2>


                        <p>

                            Batch:

                            <strong>
                                ${
                                    batch.batch_code ||
                                    batchCode
                                }
                            </strong>

                        </p>

                    </div>


                    <div
                        class="verification-badge ${
                            chainValid
                                ? "verified"
                                : "tampered"
                        }">

                        ${
                            chainValid
                                ? "✓ VERIFIED"
                                : "⚠ TAMPERED"
                        }

                    </div>


                </div>


                <!-- BASIC INFORMATION -->

                <div class="verification-grid">


                    <div class="verification-card">

                        <span>
                            Beekeeper
                        </span>

                        <strong>
                            ${
                                beekeeper.name ||
                                "N/A"
                            }
                        </strong>

                    </div>


                    <div class="verification-card">

                        <span>
                            Cluster
                        </span>

                        <strong>
                            ${
                                cluster.name ||
                                "N/A"
                            }
                        </strong>

                    </div>


                    <div class="verification-card">

                        <span>
                            Harvest Date
                        </span>

                        <strong>
                            ${
                                batch.harvest_date ||
                                "N/A"
                            }
                        </strong>

                    </div>


                    <div class="verification-card">

                        <span>
                            Quantity
                        </span>

                        <strong>
                            ${
                                batch.quantity_kg ??
                                "N/A"
                            } kg
                        </strong>

                    </div>


                </div>


                <!-- LAB RESULT -->

                <div class="verification-section">

                    <h3>
                        🧪 Laboratory Result
                    </h3>


                    ${
                        labTests.length > 0

                            ? labTests
                                .map(
                                    test => `

                                        <div class="lab-result">

                                            <strong>
                                                ${
                                                    test.purity_status ||
                                                    "N/A"
                                                }
                                            </strong>


                                            <span>

                                                Moisture:

                                                ${
                                                    test.moisture_percent ??
                                                    "N/A"
                                                }%

                                            </span>


                                            <p>
                                                ${
                                                    test.test_result ||
                                                    ""
                                                }
                                            </p>

                                        </div>

                                    `
                                )
                                .join("")

                            : `

                                <p>
                                    No laboratory record available.
                                </p>

                            `
                    }

                </div>


                <!-- AI HEALTH -->

                <div class="verification-section">

                    <h3>
                        🤖 Hive Health at Harvest
                    </h3>


                    ${
                        aiHealth

                            ? `

                                <div class="health-result">

                                    <strong>
                                        ${
                                            aiHealth.health_status ||
                                            "N/A"
                                        }
                                    </strong>


                                    <span>

                                        Health Score:

                                        ${
                                            aiHealth.health_score ??
                                            "N/A"
                                        }

                                    </span>


                                    <span>

                                        Risk:

                                        ${
                                            aiHealth.risk_indicator ||
                                            "N/A"
                                        }

                                    </span>

                                </div>

                            `

                            : `

                                <p>
                                    No AI health record available.
                                </p>

                            `
                    }

                </div>


                <!-- TRACEABILITY -->

                <div class="verification-section">

                    <h3>
                        🔗 Traceability
                    </h3>


                    <div class="verification-chain">


                        ${
                            traceability.length > 0

                                ? traceability
                                    .map(
                                        (
                                            event,
                                            index
                                        ) => `

                                            <div class="chain-event">


                                                <span>
                                                    ${
                                                        index + 1
                                                    }
                                                </span>


                                                <div>

                                                    <strong>
                                                        ${
                                                            event.event_type
                                                        }
                                                    </strong>


                                                    <p>
                                                        ${
                                                            event.location ||
                                                            "N/A"
                                                        }
                                                    </p>

                                                </div>


                                            </div>

                                        `
                                    )
                                    .join("")

                                : `

                                    <p>
                                        No traceability events found.
                                    </p>

                                `
                        }


                    </div>

                </div>


                <!-- CRYPTOGRAPHIC STATUS -->

                <div class="cryptographic-status">


                    <strong>

                        ${
                            chainValid

                                ? "✓ Traceability chain integrity confirmed"

                                : "⚠ Traceability chain integrity failed"
                        }

                    </strong>


                    <p>

                        This confirms the integrity of the
                        recorded traceability data.

                    </p>


                </div>


            </div>

        `;


    } catch (error) {

        console.error(
            "Verification error:",
            error
        );


        resultContainer.innerHTML = `

            <div class="verification-error">

                Unable to verify this batch.

            </div>

        `;
    }
}


// ============================================================
// GENERIC ELEMENT UPDATER
// ============================================================

function updateElement(
    id,
    value,
    suffix = ""
) {

    const element =
        document.getElementById(id);


    if (!element) {

        console.warn(
            `UI element not found for: ${id}`
        );

        return;
    }


    element.textContent =
        `${value}${suffix}`;
}


// ============================================================
// NAVIGATION
// ============================================================

function setupNavigation() {

    const navButtons =
        document.querySelectorAll(
            "[data-page]"
        );


    navButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const pageName =
                        button.dataset.page;


                    showPage(
                        pageName
                    );


                    navButtons.forEach(
                        btn => {
                            btn.classList.remove(
                                "active"
                            );
                        }
                    );


                    button.classList.add(
                        "active"
                    );
                }
            );

        }
    );
}


// ============================================================
// SHOW PAGE
// ============================================================

function showPage(
    pageName,
    button = null
) {

    const pages =
        document.querySelectorAll(
            ".page"
        );


    pages.forEach(
        page => {

            page.classList.remove(
                "active-page"
            );

        }
    );


    const target =
        document.getElementById(
            pageName
        );


    if (target) {

        target.classList.add(
            "active-page"
        );

    } else {

        console.warn(
            `Page not found: ${pageName}`
        );
    }


    // Update sidebar

    const navButtons =
        document.querySelectorAll(
            ".nav-item"
        );


    navButtons.forEach(
        btn => {

            btn.classList.remove(
                "active"
            );

        }
    );


    if (button) {

        button.classList.add(
            "active"
        );

    }
}


// ============================================================
// SHOW PAGE BY NAME
// ============================================================

function showPageByName(
    pageName
) {

    showPage(
        pageName
    );


    const navButtons =
        document.querySelectorAll(
            ".nav-item"
        );


    navButtons.forEach(
        button => {

            button.classList.remove(
                "active"
            );


            const onclick =
                button.getAttribute(
                    "onclick"
                );


            if (
                onclick &&
                onclick.includes(
                    `'${pageName}'`
                )
            ) {

                button.classList.add(
                    "active"
                );

            }

        }
    );
}


// ============================================================
// OPEN VERIFICATION FROM QR
// ============================================================

async function openVerificationFromQR() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    const batchCode =
        params.get("batch");


    if (!batchCode) {
        return;
    }


    console.log(
        "QR verification detected:",
        batchCode
    );


    const input =
        document.getElementById(
            "verify-batch-code"
        );


    if (input) {

        input.value =
            batchCode;

    }


    showPage(
        "verification"
    );


    await verifyHoney();
}


// ============================================================
// INITIALIZE DASHBOARD
// ============================================================

async function initializeDashboard() {

    console.log(
        "🍯 Honey Chain dashboard starting..."
    );


    // Backend status

    await checkBackendStatus();


    // Navigation

    setupNavigation();


    // Hive

    await loadHiveData();


    // Live sensors

    await loadSensorData();


    // AI health

    await loadHealthData();


    // Yield prediction

    await loadYieldPrediction();


    // Honey batches

    await loadBatches();


    // Traceability

    await loadTraceability();


    // KVIC clusters

    await loadClusters();


    // QR verification

    await openVerificationFromQR();


    console.log(
        "✅ Dashboard initialization complete."
    );
}


// ============================================================
// START APPLICATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);


// ============================================================
// LIVE REFRESH
// ============================================================

setInterval(
    async () => {

        await loadSensorData();

        await loadHealthData();

        await loadYieldPrediction();

    },
    5000
);


// ============================================================
// MAKE FUNCTIONS AVAILABLE TO HTML ONCLICK
// ============================================================
//
// This makes inline HTML buttons such as:
// onclick="showPage('dashboard')"
// onclick="generateBatchQR(1)"
// onclick="verifyHoney()"
// work reliably.
//

window.showPage =
    showPage;

window.showPageByName =
    showPageByName;

window.generateBatchQR =
    generateBatchQR;

window.closeQRPopup =
    closeQRPopup;

window.viewBatchTraceability =
    viewBatchTraceability;

window.verifyHoney =
    verifyHoney;

window.loadBatches =
    loadBatches;

window.handleQRImageError =
    handleQRImageError;