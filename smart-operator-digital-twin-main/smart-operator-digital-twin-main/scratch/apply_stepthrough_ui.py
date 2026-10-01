import re

app_file = r"c:\Users\91849\Downloads\smart-operator-digital-twin-main\app.py"

with open(app_file, "r", encoding="utf-8") as f:
    code = f.read()

new_func = '''def render_operator_assistant_view(current_record, current_state, highest_priority_recommendation, decisions):
    """
    Renders the In-Cab, Glove-Friendly Operator Assistant interface.
    Refactored with glanceable step-through interaction patterns:
    - Default view = 1 glanceable state.
    - Multi-item features (Checklist, Training) = step-through 1 item at a time.
    """

    # ------------------------------------------------------------
    # CENTRALIZED AUTOMATED ESCALATION CONFIGURATION
    # ------------------------------------------------------------
    ESCALATION_CONFIG = {
        "SAFETY_SCORE_MIN_THRESHOLD": 70,       # Escalates if composite safety score < 70
        "RED_PROXIMITY_ENABLED": True,          # Escalates on Red-zone proximity breach (< 3.0m)
        "REPEATED_AMBER_COUNT": 2,              # Escalates if >= 2 Amber proximity events in shift
        "SEATBELT_ACTIVE_OP_ENABLED": True,    # Escalates if seatbelt unfastened during active operation
        "FATIGUE_TAKE_BREAK_ENABLED": True      # Escalates if fatigue status == "TAKE A BREAK" (< 65 score)
    }

    # ------------------------------------------------------------
    # GLOBAL CONVERSION & SAFETY CONSTANTS
    # ------------------------------------------------------------
    DIESEL_CO2_PER_LITER = 2.68   # kg CO2 per liter of diesel fuel
    CAR_KM_PER_KG_CO2 = 6.0       # km driven in standard passenger car per kg CO2
    
    STANDARD_SPEED_LIMIT = 5.0    # km/h safe machine travel limit
    HAZARD_SPEED_LIMIT = 2.0      # km/h safe speed near active hazard zone

    idle_mins = float(current_state.operation.idle_time_minutes)

    # ------------------------------------------------------------
    # SESSION STATE INITIALIZATION
    # ------------------------------------------------------------
    if "op_assistant_nav" not in st.session_state:
        st.session_state.op_assistant_nav = "📋 Shift Tasks"

    if "active_task_idx" not in st.session_state:
        st.session_state.active_task_idx = 0

    if "active_preop_idx" not in st.session_state:
        st.session_state.active_preop_idx = 0

    if "active_train_idx" not in st.session_state:
        st.session_state.active_train_idx = 0

    if "dismissed_nudges" not in st.session_state:
        st.session_state.dismissed_nudges = set()

    if "incident_cooldowns" not in st.session_state:
        st.session_state.incident_cooldowns = {}

    if "safety_score_history" not in st.session_state:
        st.session_state.safety_score_history = [95, 94, 92]

    if "shift_tasks" not in st.session_state:
        st.session_state.shift_tasks = [
            {"id": 1, "name": "Trenching Zone B-4 (Section 12)", "zone": "Zone B-4", "est_min": 90, "elapsed_min": 58, "status": "In-Progress"},
            {"id": 2, "name": "Foundation Earthmoving - North Block", "zone": "North Block", "est_min": 120, "elapsed_min": 0, "status": "Pending"},
            {"id": 3, "name": "Stockpile Loading - Truck Fleet #4", "zone": "Stockpile A", "est_min": 45, "elapsed_min": 45, "status": "Completed"},
            {"id": 4, "name": "Access Road Leveling & Grading", "zone": "Access Sector 2", "est_min": 60, "elapsed_min": 0, "status": "Pending"},
        ]

    if "incident_log" not in st.session_state:
        st.session_state.incident_log = [
            {"time": "08:15 AM", "type": "Seatbelt Reminder", "severity": "WARNING", "category": "HEALTH & SAFETY", "impact": "-10 pts", "details": "Operator seatbelt unfastened for 12 seconds during start."},
            {"time": "07:30 AM", "type": "Pre-Start Inspection", "severity": "INFO", "category": "HEALTH & SAFETY", "impact": "0 pts", "details": "Daily fluid level and hydraulic hose inspection completed."},
        ]

    if "escalations" not in st.session_state:
        st.session_state.escalations = [
            {
                "id": "esc_init_1",
                "time": "08:15 AM",
                "step": 0,
                "operator": "Alex M.",
                "machine_id": current_state.machine_id,
                "trigger": "Seatbelt Unfastened During Active Operation",
                "severity": "CRITICAL",
                "status": "Acknowledged",
                "ack_time": "08:17 AM",
                "res_time": None
            }
        ]

    if "escalation_cooldowns" not in st.session_state:
        st.session_state.escalation_cooldowns = {}

    if "amber_event_count" not in st.session_state:
        st.session_state.amber_event_count = 0

    # 15-Item Pre-Operation Cab Checklist Definition
    PRE_OP_CHECKLIST_ITEMS = [
        {"id": "fluid_levels", "name": "Engine Oil & Coolant Fluid Levels", "cat": "Fluids & Engine", "desc": "Check engine dipstick, coolant level, and radiator overflow reservoir."},
        {"id": "undercarriage", "name": "Tracks / Tires / Undercarriage Condition", "cat": "Mechanical", "desc": "Inspect track tension, shoes, rollers, sprockets, or tire tread inflation."},
        {"id": "seatbelt_mirrors", "name": "Seatbelt Buckle & Rearview Mirrors", "cat": "Cab & Safety", "desc": "Ensure seatbelt latch locks securely and mirrors are aligned for clear rear view."},
        {"id": "lights_alarms", "name": "Dashboard Warning Lights & Alarms", "cat": "Electrical", "desc": "Verify bulb self-test pass and audible travel warning chime sounds."},
        {"id": "fire_ext", "name": "Fire Extinguisher Charge & Mounting", "cat": "Safety Equipment", "desc": "Gauge in green zone, quick-release pin intact."},
        {"id": "guards_shields", "name": "Safety Guards & Structural Shields", "cat": "Mechanical", "desc": "Confirm engine side compartment panels and hydraulic pump shields are locked."},
        {"id": "hydraulic_hoses", "name": "Hydraulic Hoses & Cylinder Integrity", "cat": "Hydraulics", "desc": "Inspect boom, arm, and bucket cylinder hoses for weeping oil, bulges, or chafing."},
        {"id": "visible_leaks", "name": "Ground Leak Check under Machine", "cat": "Fluids & Engine", "desc": "Look under machine belly pan for fresh oil, fuel, or coolant drips."},
        {"id": "glass_visibility", "name": "Cab Glass Cleanliness & Wipers", "cat": "Cab & Safety", "desc": "Wipe front windshield glass clean and confirm washer fluid reservoir filled."},
        {"id": "horn_function", "name": "Horn & Travel Warning Signal", "cat": "Electrical", "desc": "Test cab steering wheel horn button and 2-tone travel warning alarm."},
        {"id": "backup_camera", "name": "Backup Camera & Perimeter Display", "cat": "Safety Equipment", "desc": "Verify rear camera feed image clarity on the main cab tablet display screen."},
        {"id": "work_lights", "name": "LED Work Lights & Hazard Flashers", "cat": "Electrical", "desc": "Turn on boom floodlights, cab roof lights, and orange strobe beacon."},
        {"id": "cab_controls", "name": "Joystick & Hydraulic Lock Lever", "cat": "Cab & Controls", "desc": "Confirm red hydraulic lockout lever smoothly engages and disengages pilot controls."},
        {"id": "parking_brake", "name": "Parking Brake & Swing Lock Pin", "cat": "Cab & Controls", "desc": "Engage house swing lock pin and verify parking brake holds machine steady."},
        {"id": "walk_check", "name": "360° Walk-Around Perimeter Clearance", "cat": "Site Safety", "desc": "Perform 360-degree walk around machine to clear ground workers, tools, and obstacles."}
    ]

    if "pre_op_status" not in st.session_state:
        st.session_state.pre_op_status = {item["id"]: "PASSED" for item in PRE_OP_CHECKLIST_ITEMS}

    if "pre_op_notes" not in st.session_state:
        st.session_state.pre_op_notes = {}

    if "training_modules" not in st.session_state:
        st.session_state.training_modules = [
            {
                "id": "mod_1",
                "title": "Module 1: Proximity Hazard Mitigation",
                "category": "HEALTH & SAFETY",
                "scenario": "You are trenching near Zone B-4 when your perimeter display flags a site pickup truck 6.2m on your right side.",
                "options": [
                    "A) Continue digging at full speed since it's outside the 3m red zone.",
                    "B) Reduce speed (< 2 km/h), sound horn, and confirm truck position via radio before moving.",
                    "C) Swing boom right immediately to signal the truck to leave."
                ],
                "correct_idx": 1,
                "explanation": "Reducing machine speed to the hazard limit (2.0 km/h) and establishing positive radio contact prevents swing-radius collisions.",
                "user_answer": 1,
                "status": "Passed"
            },
            {
                "id": "mod_2",
                "title": "Module 2: Inclined Ramp Overspeed Control",
                "category": "HEALTH & SAFETY",
                "scenario": "While traveling down a 12% grade access ramp, machine speed hits 6.8 km/h (speed limit: 5.0 km/h) and an overspeed alert sounds.",
                "options": [
                    "A) Apply service brake smoothly, lower engine RPM, and maintain speed under 5 km/h.",
                    "B) Shift travel control into neutral and let gravity coast the machine down.",
                    "C) Lower the excavator bucket onto the gravel ramp surface to drag brake."
                ],
                "correct_idx": 0,
                "explanation": "Controlled service braking combined with lower engine RPM maintains traction without overheating hydraulic brakes or chattering tracks.",
                "user_answer": 0,
                "status": "Passed"
            },
            {
                "id": "mod_3",
                "title": "Module 3: Idle Fuel & Emission Reduction",
                "category": "OPERATING EFFICIENCY",
                "scenario": "You arrive at stockpile loader zone and are informed of a 30-minute truck queue delay. Engine fuel level is at 22%.",
                "options": [
                    "A) Keep engine idling at 1900 RPM to keep cab air conditioning cold.",
                    "B) Leave engine idling at low idle (800 RPM) for the entire 30 minutes.",
                    "C) Shut off engine after 3 minutes of waiting to eliminate wasted fuel and emissions, notifying dispatch."
                ],
                "correct_idx": 2,
                "explanation": "Shutting down during waits > 5 mins saves ~4.5L of diesel per hour, prevents ~12 kg of CO₂ emissions, and extends engine component life.",
                "user_answer": 2,
                "status": "Passed"
            },
            {
                "id": "mod_4",
                "title": "Module 4: Hydraulic Over-Pressure Relief",
                "category": "OPERATING EFFICIENCY",
                "scenario": "While digging in rocky clay, hydraulic pressure spikes above 300 bar and machine health drops by 2%.",
                "options": [
                    "A) Pull joystick harder to force the bucket through the rock seam.",
                    "B) Ease joystick pressure, adjust bucket entry angle, and use hydraulic hammer attachment if needed.",
                    "C) Turn off engine immediately while bucket is stuck in the trench."
                ],
                "correct_idx": 1,
                "explanation": "Adjusting bucket entry angle prevents continuous hydraulic relief valve bypass venting, lowering oil temperature and preserving pump life.",
                "user_answer": None,
                "status": "Not Started"
            }
        ]

    # ------------------------------------------------------------
    # THREE-ZONE PROXIMITY SAFETY SYSTEM
    # Thresholds: GREEN (>10.0m), AMBER (3.0m - 10.0m), RED (<3.0m)
    # ------------------------------------------------------------
    has_hazard = current_state.anomaly_detected or current_state.scenario == "SAFETY_VIOLATION"
    has_warning = current_state.overall_status == "WARNING"

    if has_hazard:
        hazard_dir = "REAR"
        hazard_dist = 2.4
        hazard_zone = "RED"
        hazard_label = "RED DANGER: Ground worker detected 2.4m behind rear counterweight swing zone!"
    elif has_warning:
        hazard_dir = "RIGHT"
        hazard_dist = 6.2
        hazard_zone = "AMBER"
        hazard_label = "AMBER CAUTION: Site pickup truck parked 6.2m near right track."
    else:
        hazard_dir = "NONE"
        hazard_dist = 12.5
        hazard_zone = "GREEN"
        hazard_label = "GREEN SAFE: All 4 perimeter zones clear (> 10.0m)."

    # ------------------------------------------------------------
    # OVERSPEED DETECTION & COMPOSITE SAFETY SCORE (0-100)
    # ------------------------------------------------------------
    speed_kmh = float(current_state.operation.speed_kmh)
    active_speed_limit = HAZARD_SPEED_LIMIT if hazard_zone in ["AMBER", "RED"] else STANDARD_SPEED_LIMIT
    is_overspeed = speed_kmh > active_speed_limit

    score_deductions = []

    if not current_state.safety.seatbelt_fastened and current_state.safety.operator_present:
        score_deductions.append({"issue": "Seatbelt Violation", "pts": -10, "details": "Seatbelt unfastened while in operator seat"})

    if is_overspeed:
        score_deductions.append({"issue": "Overspeed Event", "pts": -8, "details": f"Speed {speed_kmh:.1f} km/h exceeded limit ({active_speed_limit:.1f} km/h)"})

    if hazard_zone == "RED":
        score_deductions.append({"issue": "Proximity RED Danger", "pts": -12, "details": f"Ground worker 2.4m near {hazard_dir} zone"})
    elif hazard_zone == "AMBER":
        score_deductions.append({"issue": "Proximity AMBER Caution", "pts": -4, "details": f"Obstacle 6.2m near {hazard_dir} zone"})

    if current_state.operation.idle_time_minutes > 15:
        score_deductions.append({"issue": "Excessive Idling", "pts": -5, "details": f"Idling for {current_state.operation.idle_time_minutes:.0f} mins (>15m threshold)"})

    # Pre-Op Checklist & Training Impact on Composite Safety Score
    pre_op_passed_count = sum(1 for status in st.session_state.pre_op_status.values() if status == "PASSED")
    pre_op_flagged_count = sum(1 for status in st.session_state.pre_op_status.values() if status == "ISSUE_FLAGGED")
    pre_op_complete = (pre_op_passed_count + pre_op_flagged_count) == len(PRE_OP_CHECKLIST_ITEMS)
    pre_op_all_clean = pre_op_complete and pre_op_flagged_count == 0

    if pre_op_flagged_count > 0:
        score_deductions.append({"issue": "Pre-Op Inspection Defect", "pts": -5, "details": f"{pre_op_flagged_count} pre-op item(s) flagged with issues"})
    elif not pre_op_complete:
        score_deductions.append({"issue": "Incomplete Pre-Op Inspection", "pts": -3, "details": f"Pre-op checklist incomplete ({pre_op_passed_count}/{len(PRE_OP_CHECKLIST_ITEMS)})"})

    passed_training_count = sum(1 for m in st.session_state.training_modules if m["status"] == "Passed")
    training_bonus = 3 if passed_training_count >= 3 else 0
    pre_op_bonus = 5 if pre_op_all_clean else 0

    total_deduction = sum(item["pts"] for item in score_deductions)
    composite_safety_score = max(35, min(100, 100 + total_deduction + pre_op_bonus + training_bonus))

    # Track safety score trend
    st.session_state.safety_score_history.append(composite_safety_score)
    if len(st.session_state.safety_score_history) > 10:
        st.session_state.safety_score_history.pop(0)

    recent_scores = st.session_state.safety_score_history
    if len(recent_scores) >= 2:
        if recent_scores[-1] > recent_scores[-2]:
            score_trend = "RISING ↗️"
        elif recent_scores[-1] < recent_scores[-2]:
            score_trend = "DECLINING ↘️"
        else:
            score_trend = "STABLE ➡️"
    else:
        score_trend = "STABLE ➡️"

    if composite_safety_score >= 88:
        score_status = "EXCELLENT"
        score_color = "#166534"
        score_bg = "#dcfce7"
        score_icon = "🟢"
    elif composite_safety_score >= 70:
        score_status = "GOOD"
        score_color = "#92400e"
        score_bg = "#fef3c7"
        score_icon = "🟡"
    else:
        score_status = "NEEDS ATTENTION"
        score_color = "#991b1b"
        score_bg = "#fee2e2"
        score_icon = "🔴"

    # Incident Logging with 5-Step Cooldown Window
    current_sim_step = st.session_state.record_number
    cooldown_steps = 5

    for ded in score_deductions:
        issue_key = ded["issue"]
        last_step = st.session_state.incident_cooldowns.get(issue_key, -999)
        if (current_sim_step - last_step) >= cooldown_steps:
            is_eff = issue_key in ["Excessive Idling"]
            st.session_state.incident_log.insert(0, {
                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                "type": issue_key,
                "severity": "CRITICAL" if ded["pts"] <= -10 else "WARNING",
                "category": "OPERATING EFFICIENCY" if is_eff else "HEALTH & SAFETY",
                "impact": f"{ded['pts']} pts",
                "details": ded["details"]
            })
            st.session_state.incident_cooldowns[issue_key] = current_sim_step

    # ------------------------------------------------------------
    # EVALUATE AUTOMATED ESCALATION TRIGGERS FOR SUPERVISOR
    # ------------------------------------------------------------
    active_triggers = []

    if composite_safety_score < ESCALATION_CONFIG["SAFETY_SCORE_MIN_THRESHOLD"]:
        active_triggers.append({
            "key": "low_safety_score",
            "trigger": f"Low Safety Score ({composite_safety_score}/100 < {ESCALATION_CONFIG['SAFETY_SCORE_MIN_THRESHOLD']} threshold)",
            "severity": "CRITICAL"
        })

    if ESCALATION_CONFIG["RED_PROXIMITY_ENABLED"] and hazard_zone == "RED":
        active_triggers.append({
            "key": "red_proximity",
            "trigger": f"Red-Zone Proximity Danger ({hazard_dist}m breach in {hazard_dir} zone)",
            "severity": "CRITICAL"
        })

    if ESCALATION_CONFIG["SEATBELT_ACTIVE_OP_ENABLED"] and (not current_state.safety.seatbelt_fastened and current_state.safety.operator_present):
        active_triggers.append({
            "key": "seatbelt_violation",
            "trigger": "Seatbelt Unfastened During Active Operation",
            "severity": "CRITICAL"
        })

    # FATIGUE MODEL
    rec_num = st.session_state.record_number
    shift_hours = ((rec_num % 480) / 60.0) + 1.5
    idle_penalty = min(20.0, (current_state.operation.idle_time_minutes / 20.0) * 15.0)
    base_alertness = 100.0 - (shift_hours * 4.0) - idle_penalty
    if current_state.anomaly_detected:
        base_alertness -= 8.0
    alertness_score = max(45.0, min(99.0, base_alertness))

    if alertness_score >= 82:
        fatigue_status = "ALERT & FOCUSED"
        fatigue_color = "#166534"
        fatigue_bg = "#dcfce7"
        fatigue_icon = "🟢"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift with steady operational pace."
    elif alertness_score >= 65:
        fatigue_status = "GETTING TIRED"
        fatigue_color = "#92400e"
        fatigue_bg = "#fef3c7"
        fatigue_icon = "🟡"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift with elevated idle ratio. Consider a 5-min stretch break."
    else:
        fatigue_status = "TAKE A BREAK"
        fatigue_color = "#991b1b"
        fatigue_bg = "#fee2e2"
        fatigue_icon = "🔴"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift — high fatigue risk detected. Mandatory 15-min break recommended."

    if ESCALATION_CONFIG["FATIGUE_TAKE_BREAK_ENABLED"] and fatigue_status == "TAKE A BREAK":
        active_triggers.append({
            "key": "fatigue_break",
            "trigger": f"Critical Operator Fatigue (Alertness: {alertness_score:.0f}% - Mandatory Break)",
            "severity": "WARNING"
        })

    if hazard_zone == "AMBER":
        st.session_state.amber_event_count += 1
        if st.session_state.amber_event_count >= ESCALATION_CONFIG["REPEATED_AMBER_COUNT"]:
            active_triggers.append({
                "key": "repeated_amber",
                "trigger": f"Repeated Amber-Zone Proximity Events ({st.session_state.amber_event_count} events in shift)",
                "severity": "WARNING"
            })
    else:
        st.session_state.amber_event_count = 0

    for trg in active_triggers:
        last_step = st.session_state.escalation_cooldowns.get(trg["key"], -999)
        if (current_sim_step - last_step) >= 10:
            esc_item = {
                "id": f"esc_{len(st.session_state.escalations)+1}_{current_sim_step}",
                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                "step": current_sim_step,
                "operator": "Alex M.",
                "machine_id": current_state.machine_id,
                "trigger": trg["trigger"],
                "severity": trg["severity"],
                "status": "Active",
                "ack_time": None,
                "res_time": None
            }
            st.session_state.escalations.insert(0, esc_item)
            st.session_state.escalation_cooldowns[trg["key"]] = current_sim_step

    # Task progress % computation
    for task in st.session_state.shift_tasks:
        if task["status"] == "Completed":
            task["progress"] = 100
        elif task["status"] == "Pending":
            task["progress"] = 0
        else:
            task["progress"] = min(99, max(5, int((task["elapsed_min"] / max(1, task["est_min"])) * 100)))

    # IN-CAB HEADER BAR
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 1.2rem 1.6rem; border-radius: 20px; color: white; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
            <div>
                <span style="font-size: 1.6rem; font-weight: 900; letter-spacing: 0.5px;">👷 SMART OPERATOR CAB</span>
                <span style="color: #94a3b8; font-size: 1rem; margin-left: 1rem;">| {current_state.machine_id} (Alex M.)</span>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <div style="background-color: {score_bg}; color: {score_color}; font-weight: 800; padding: 0.5rem 1.2rem; border-radius: 999px; font-size: 1.1rem;">
                    {score_icon} SAFETY SCORE: {composite_safety_score} ({score_status})
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2-COLUMN LAYOUT
    nav_col, main_col = st.columns([1.1, 3.9])

    with nav_col:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 800; color: #64748b; margin-bottom: 0.5rem;'>CAB MENU</div>", unsafe_allow_html=True)
        
        nav_options = [
            "📋 Shift Tasks",
            "🦺 Safety & Hazard Radar",
            "🌱 Fuel & Pattern Alerts",
            "🎓 Training & Pre-Op Hub",
            "🤖 Shift Summary",
            "📊 Fleet Overview"
        ]

        selected_nav = st.radio(
            "Navigation Menu",
            nav_options,
            index=nav_options.index(st.session_state.op_assistant_nav),
            key="op_assistant_nav_radio",
            label_visibility="collapsed"
        )
        st.session_state.op_assistant_nav = selected_nav

    with main_col:
        # LIVE IN-THE-MOMENT COACHING NUDGES
        active_nudge = None
        if hazard_zone == "RED" and "proximity_red_nudge" not in st.session_state.dismissed_nudges:
            active_nudge = {
                "id": "proximity_red_nudge",
                "cat": "HEALTH & SAFETY",
                "icon": "🚨",
                "text": f"PROXIMITY DANGER: Ground worker detected 2.4m behind REAR swing zone!",
                "bg": "#fee2e2", "fg": "#991b1b"
            }
        elif hazard_zone == "AMBER" and "proximity_amber_nudge" not in st.session_state.dismissed_nudges:
            active_nudge = {
                "id": "proximity_amber_nudge",
                "cat": "HEALTH & SAFETY",
                "icon": "⚠️",
                "text": f"PROXIMITY CAUTION: Site pickup truck 6.2m near RIGHT track.",
                "bg": "#fef3c7", "fg": "#92400e"
            }
        elif is_overspeed and "overspeed_nudge" not in st.session_state.dismissed_nudges:
            active_nudge = {
                "id": "overspeed_nudge",
                "cat": "HEALTH & SAFETY",
                "icon": "🏎️",
                "text": f"Overspeed Warning: Machine speed ({speed_kmh:.1f} km/h) exceeds safe limit ({active_speed_limit:.1f} km/h).",
                "bg": "#fee2e2", "fg": "#991b1b"
            }
        elif not current_state.safety.seatbelt_fastened and "seatbelt_nudge" not in st.session_state.dismissed_nudges:
            active_nudge = {
                "id": "seatbelt_nudge",
                "cat": "HEALTH & SAFETY",
                "icon": "🚨",
                "text": "Safety Nudge: Buckle seatbelt before initiating boom travel.",
                "bg": "#fee2e2", "fg": "#991b1b"
            }

        if active_nudge:
            nc1, nc2 = st.columns([5.5, 1])
            with nc1:
                cat_badge = f"<span style='background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;'>⚡ OPERATING EFFICIENCY</span>" if active_nudge["cat"] == "OPERATING EFFICIENCY" else f"<span style='background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;'>🛡️ HEALTH & SAFETY</span>"
                st.markdown(
                    f"""
                    <div style="background-color: {active_nudge['bg']}; color: {active_nudge['fg']}; padding: 0.9rem 1.2rem; border-radius: 14px; font-weight: 700; font-size: 1.05rem; display: flex; align-items: center;">
                        {cat_badge} {active_nudge['icon']} {active_nudge['text']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with nc2:
                if st.button("✖ DISMISS", key=f"dismiss_{active_nudge['id']}", use_container_width=True):
                    st.session_state.dismissed_nudges.add(active_nudge['id'])
                    st.rerun()

            st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)

        # SECTION 1: 📋 SHIFT TASKS
        if st.session_state.op_assistant_nav == "📋 Shift Tasks":
            st.markdown("## 📋 Active Shift Task Focus")
            
            # GATING CHECK: Pre-op checklist must be fully completed and passed without flagged issues
            if not pre_op_complete or pre_op_flagged_count > 0:
                st.markdown(
                    f"""
                    <div style="background-color: #fee2e2; border: 3px solid #ef4444; border-radius: 18px; padding: 1.2rem; margin-bottom: 1.2rem;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span style="font-size: 2.5rem;">🚫</span>
                            <div>
                                <span style="background:#991b1b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">SHIFT START LOCKED</span>
                                <div style="font-size: 1.3rem; font-weight: 900; color: #991b1b; margin-top:0.2rem;">PRE-OPERATION CHECKLIST INCOMPLETE OR HAS FLAGGED DEFECTS</div>
                                <div style="color: #b91c1c; font-size: 1.05rem; font-weight: 700; margin-top: 0.3rem;">
                                    Completed: {pre_op_passed_count}/{len(PRE_OP_CHECKLIST_ITEMS)} items passed | Flagged defects: {pre_op_flagged_count}. Resolve flagged items in the <strong>🎓 Training & Pre-Op Hub</strong> before starting shift tasks.
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            tasks = st.session_state.shift_tasks
            idx = st.session_state.active_task_idx % len(tasks)
            active_task = tasks[idx]

            step_c1, step_c2, step_c3 = st.columns([1, 2, 1])
            with step_c1:
                if st.button("⬅ PREVIOUS TASK", use_container_width=True, key="prev_task_btn"):
                    st.session_state.active_task_idx = (idx - 1) % len(tasks)
                    st.rerun()
            with step_c2:
                st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>TASK {idx + 1} OF {len(tasks)}</div>", unsafe_allow_html=True)
            with step_c3:
                if st.button("NEXT TASK ➔", use_container_width=True, key="next_task_btn"):
                    st.session_state.active_task_idx = (idx + 1) % len(tasks)
                    st.rerun()

            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                t_badge_bg = "#dcfce7" if active_task['status'] == "Completed" else ("#fef3c7" if active_task['status'] == "In-Progress" else "#f1f5f9")
                t_badge_fg = "#166534" if active_task['status'] == "Completed" else ("#92400e" if active_task['status'] == "In-Progress" else "#475569")
                
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; border-radius: 16px; padding: 1.5rem; border: 1px solid #e2e8f0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;">⚡ OPERATING EFFICIENCY</span>
                                <span style="font-size: 1.8rem; font-weight: 900; color: #0f172a;">{active_task['name']}</span>
                            </div>
                            <span style="font-size: 1.2rem; font-weight: 800; padding: 0.6rem 1.4rem; border-radius: 999px; background-color: {t_badge_bg}; color: {t_badge_fg};">
                                {active_task['status'].upper()}
                            </span>
                        </div>
                        <div style="font-size: 1.1rem; color: #64748b; margin-top: 0.6rem;">
                            📍 <strong>Location:</strong> {active_task['zone']} &nbsp;|&nbsp; ⏱️ <strong>Target Duration:</strong> {active_task['est_min']} Minutes &nbsp;|&nbsp; ⏳ <strong>Elapsed:</strong> {active_task['elapsed_min']} Min
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.progress(active_task['progress'] / 100.0, text=f"Task Completion (Time Elapsed vs Target): {active_task['progress']}%")

                st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)
                st.markdown("##### 👆 QUICK TAP STATUS TOGGLE")
                
                st_c1, st_c2, st_c3 = st.columns(3)
                with st_c1:
                    if st.button("⏳ MARK PENDING", use_container_width=True, key=f"t_pend_{idx}"):
                        active_task['status'] = "Pending"
                        st.rerun()
                with st_c2:
                    if st.button("▶ MARK IN-PROGRESS", use_container_width=True, key=f"t_inprog_{idx}"):
                        if not pre_op_complete or pre_op_flagged_count > 0:
                            st.error("🚫 Cannot start shift task! Resolve flagged items in Pre-Op Checklist first.")
                        else:
                            active_task['status'] = "In-Progress"
                            st.rerun()
                with st_c3:
                    if st.button("✅ MARK COMPLETED", use_container_width=True, key=f"t_comp_{idx}"):
                        active_task['status'] = "Completed"
                        active_task['progress'] = 100
                        st.rerun()

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("### 📊 Shift Task Summary Grid")
            
            for i, t in enumerate(tasks):
                is_curr = (i == idx)
                border_color = "#0284c7" if is_curr else "#cbd5e1"
                bg_color = "#f0f9ff" if is_curr else "#ffffff"
                
                with st.container(border=True):
                    grid_c1, grid_c2, grid_c3 = st.columns([3, 1.2, 1.2])
                    with grid_c1:
                        curr_indicator = "👉 " if is_curr else ""
                        st.markdown(f"**{curr_indicator}Task {i+1}: {t['name']}**")
                        st.caption(f"Zone: {t['zone']} | Est: {t['est_min']} mins")
                    with grid_c2:
                        st.markdown(f"**Progress:** {t['progress']}%")
                    with grid_c3:
                        st.markdown(f"**Status:** `{t['status']}`")

        # SECTION 2: 🦺 SAFETY & HAZARD RADAR
        elif st.session_state.op_assistant_nav == "🦺 Safety & Hazard Radar":
            st.markdown("## 🦺 Safety & Hazard Radar System")

            # REFACTORED FEATURE 1: OPERATOR SAFETY SCORE (GLANCEABLE DEFAULT VIEW + SEE DETAILS EXPANDER)
            if score_deductions:
                worst_ded = min(score_deductions, key=lambda x: x["pts"])
                main_factor_text = f"Main factor: {worst_ded['issue']} ({worst_ded['pts']} pts)"
            elif pre_op_all_clean:
                main_factor_text = "Main factor: Clean Pre-Op Checklist (+5 pts)"
            else:
                main_factor_text = "Main factor: All operations normal"

            st.markdown(
                f"""
                <div style="background-color: {score_bg}; border: 3px solid {score_color}; border-radius: 20px; padding: 1.4rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 1.2rem;">
                            <span style="font-size: 3.5rem;">{score_icon}</span>
                            <div>
                                <span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                                <div style="font-size: 2.2rem; font-weight: 900; color: #0f172a; margin-top:0.2rem;">{composite_safety_score} <span style="font-size: 1.3rem; color: {score_color}; font-weight: 800;">— {score_status}</span></div>
                                <div style="color: {score_color}; font-size: 1.05rem; font-weight: 700;">{main_factor_text} &nbsp;|&nbsp; Trend: {score_trend}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("🔍 See details (Full Weighted Breakdown)", expanded=False):
                st.write("**Base Score:** 100 Points")
                if pre_op_all_clean:
                    st.write("🟢 **+5 Pts:** Clean Pre-Operation Checklist Passed")
                if training_bonus > 0:
                    st.write("🟢 **+3 Pts:** Training Modules Passed Bonus")
                if not score_deductions and pre_op_all_clean:
                    st.success("No safety score deductions active!")
                else:
                    for d in score_deductions:
                        st.write(f"🔴 **{d['pts']} Pts ({d['issue']}):** {d['details']}")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            # Fatigue & Alertness Card
            st.markdown(
                f"""
                <div style="background-color: {fatigue_bg}; border: 3px solid {fatigue_color}; border-radius: 20px; padding: 1.4rem; margin-bottom: 1.2rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 1.2rem;">
                            <span style="font-size: 3rem;">{fatigue_icon}</span>
                            <div>
                                <span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                                <div style="font-size: 1.6rem; font-weight: 900; color: {fatigue_color}; margin-top:0.2rem;">FATIGUE & ALERTNESS: {fatigue_status} ({alertness_score:.0f}%)</div>
                                <div style="color: {fatigue_color}; font-size: 1.05rem; font-weight: 700;">{fatigue_reason}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # REFACTORED FEATURE 2: THREE-ZONE PROXIMITY (CALM MINIMAL GREEN, COMPASS REVEALED ONLY ON AMBER/RED)
            st.markdown("### 📡 3-Zone Directional Proximity Radar")
            
            if hazard_zone == "GREEN":
                st.markdown(
                    """
                    <div style="background-color: #f0fdf4; border: 3px solid #22c55e; border-radius: 20px; padding: 1.4rem; display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1.2rem;">
                        <span style="font-size: 2.8rem;">🟢</span>
                        <div>
                            <span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                            <div style="font-size: 1.5rem; font-weight: 900; color: #166534; margin-top:0.2rem;">GREEN SAFE — ALL 4 PERIMETER ZONES CLEAR (>10.0m)</div>
                            <div style="color: #15803d; font-size: 1rem; font-weight: 600;">No ground personnel or obstacles detected near tracks or swing radius.</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                radar_bg = "#fee2e2" if hazard_zone == "RED" else "#fef3c7"
                radar_border = "#ef4444" if hazard_zone == "RED" else "#f59e0b"
                
                front_bg = '#ef4444' if hazard_dir == 'FRONT' else '#e2e8f0'
                front_fg = 'white' if hazard_dir == 'FRONT' else '#475569'
                front_txt = '🔴 2.1m' if hazard_dir == 'FRONT' else '🟢 CLEAR (>10m)'

                left_bg = '#f59e0b' if hazard_dir == 'LEFT' else '#e2e8f0'
                left_fg = 'white' if hazard_dir == 'LEFT' else '#475569'
                left_txt = '🟡 5.8m' if hazard_dir == 'LEFT' else '🟢 CLEAR (>10m)'

                right_bg = '#f59e0b' if hazard_dir == 'RIGHT' else '#e2e8f0'
                right_fg = 'white' if hazard_dir == 'RIGHT' else '#475569'
                right_txt = '🟡 6.2m' if hazard_dir == 'RIGHT' else '🟢 CLEAR (>10m)'

                rear_bg = '#ef4444' if hazard_dir == 'REAR' else '#e2e8f0'
                rear_fg = 'white' if hazard_dir == 'REAR' else '#475569'
                rear_txt = '🔴 2.4m DANGER' if hazard_dir == 'REAR' else '🟢 CLEAR (>10m)'

                st.markdown(
                    f"""
                    <div style="background-color: {radar_bg}; border: 3px solid {radar_border}; border-radius: 20px; padding: 1.5rem; margin-bottom: 1.2rem;">
                        <div style="font-size: 1.3rem; font-weight: 900; text-align: center; margin-bottom: 1rem; color: #0f172a;">{hazard_label}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 0.8rem; text-align: center; align-items: center;">
                            <div></div>
                            <div style="background: {front_bg}; color: {front_fg}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">FRONT ZONE {front_txt}</div>
                            <div></div>
                            <div style="background: {left_bg}; color: {left_fg}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">LEFT TRACK {left_txt}</div>
                            <div style="background: #1e293b; color: #f8fafc; padding: 1.2rem; border-radius: 16px; font-weight: 900; font-size: 1.1rem;">🚜 MACHINE CENTER<br/><span style="font-size:0.85rem; color:#94a3b8;">CAT EXCAVATOR</span></div>
                            <div style="background: {right_bg}; color: {right_fg}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">RIGHT TRACK {right_txt}</div>
                            <div></div>
                            <div style="background: {rear_bg}; color: {rear_fg}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">REAR SWING {rear_txt}</div>
                            <div></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Seatbelt Card
            if current_state.safety.seatbelt_fastened:
                st.markdown(
                    """
                    <div style="background-color: #f0fdf4; border: 3px solid #22c55e; border-radius: 20px; padding: 1.4rem;">
                        <div style="display: flex; align-items: center; gap: 1.2rem;">
                            <span style="font-size: 3rem;">🟢</span>
                            <div>
                                <span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                                <div style="font-size: 1.6rem; font-weight: 900; color: #166534; margin-top:0.2rem;">SEATBELT SECURE</div>
                                <div style="color: #15803d; font-size: 1.05rem; font-weight: 600;">Operator seated & safety belt buckled. Safe for operation.</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background-color: #fee2e2; border: 3px solid #ef4444; border-radius: 20px; padding: 1.4rem;">
                        <div style="display: flex; align-items: center; gap: 1.2rem;">
                            <span style="font-size: 3rem;">🚨</span>
                            <div>
                                <span style="background:#991b1b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                                <div style="font-size: 1.6rem; font-weight: 900; color: #991b1b; margin-top:0.2rem;">SAFETY VIOLATION: SEATBELT UNFASTENED (-10 PTS)</div>
                                <div style="color: #b91c1c; font-size: 1.05rem; font-weight: 700;">FASTEN SEATBELT IMMEDIATELY BEFORE OPERATING HYDRAULICS!</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Incident Log
            st.markdown("### 📝 Safety Incident Log")
            
            with st.expander("➕ REPORT SITE INCIDENT / HAZARD", expanded=False):
                with st.form("cab_incident_form"):
                    inc_type = st.selectbox("Hazard Category", ["Ground Worker In Zone", "Near-miss", "Hydraulic Warning", "Material Obstacle", "Other"])
                    inc_sev = st.radio("Severity Level", ["INFO", "WARNING", "CRITICAL"], horizontal=True)
                    inc_notes = st.text_input("Brief Details", placeholder="e.g. Worker walked near swing radius without radio call")
                    if st.form_submit_button("LOG INCIDENT NOW", use_container_width=True):
                        st.session_state.incident_log.insert(0, {
                            "time": "Just now",
                            "type": inc_type,
                            "severity": inc_sev,
                            "category": "HEALTH & SAFETY",
                            "impact": "-5 pts",
                            "details": inc_notes or "Manual report logged by operator."
                        })
                        st.success("Incident logged!")
                        st.rerun()

            for inc in st.session_state.incident_log[:5]:
                sev_icon = "🔴" if inc["severity"] == "CRITICAL" else ("🟡" if inc["severity"] == "WARNING" else "🔵")
                cat_tag_html = f"<span style='background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-right:0.5rem;'>🛡️ HEALTH & SAFETY</span>" if inc.get("category") == "HEALTH & SAFETY" else f"<span style='background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-right:0.5rem;'>⚡ OPERATING EFFICIENCY</span>"
                impact_text = f" &nbsp;|&nbsp; Impact: <strong style='color:#ef4444;'>{inc['impact']}</strong>" if "impact" in inc else ""
                with st.container(border=True):
                    st.markdown(f"{cat_tag_html} <span style='font-size: 1.1rem; font-weight: 800;'>{sev_icon} [{inc['time']}] {inc['type']}</span>{impact_text}", unsafe_allow_html=True)
                    st.write(inc["details"])

        # SECTION 3: 🌱 FUEL & PATTERN ALERTS
        elif st.session_state.op_assistant_nav == "🌱 Fuel & Pattern Alerts":
            st.markdown("## 🌱 Fuel Waste & Pattern Alerts")

            wasted_fuel_l = idle_mins * (current_state.fuel.consumption_lph / 60.0)
            co2_kg = wasted_fuel_l * DIESEL_CO2_PER_LITER
            km_equivalent = co2_kg * CAR_KM_PER_KG_CO2

            shift_history_df = df.iloc[:rec_num + 1] if not df.empty else None
            shift_baseline_idle = shift_history_df['idle_time_minutes'].mean() if shift_history_df is not None and not shift_history_df.empty else 8.5
            idle_ratio_vs_baseline = idle_mins / max(1.0, shift_baseline_idle)

            st.markdown(
                f"""
                <div style="background-color: #f0fdf4; border: 3px solid #22c55e; border-radius: 20px; padding: 1.8rem; text-align: center; margin-bottom: 1.2rem;">
                    <span style="background:#0284c7; color:white; font-size:0.8rem; font-weight:800; padding:0.25rem 0.7rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
                    <div style="font-size: 1.1rem; color: #166534; font-weight: 800; margin-top:0.4rem;">IDLE FUEL WASTE & EMISSIONS</div>
                    <div style="font-size: 3rem; font-weight: 900; color: #15803d; margin: 0.4rem 0;">
                        💨 {co2_kg:.1f} kg CO₂ WASTED
                    </div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #047857;">
                        ⛽ {wasted_fuel_l:.2f} Liters Wasted in Idle Today
                    </div>
                    <div style="margin-top: 1rem; padding: 0.8rem; background-color: #dcfce7; border-radius: 12px; font-size: 1.05rem; font-weight: 700; color: #166534;">
                        🚗 Equivalent to driving a standard passenger car for <strong>{km_equivalent:.1f} km</strong> (based on {DIESEL_CO2_PER_LITER} kg CO₂/L).
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if idle_mins > 15:
                st.markdown(
                    f"""
                    <div style="background-color: #fef3c7; border: 3px solid #f59e0b; border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem;">
                        <span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
                        <div style="font-size: 1.4rem; font-weight: 900; color: #92400e; margin-top:0.3rem;">🟡 EXCESSIVE IDLE PATTERN DETECTED</div>
                        <div style="font-size: 1.1rem; color: #78350f; margin-top: 0.4rem;">
                            Current idle time (<strong>{idle_mins:.1f} mins</strong>) is <strong>{idle_ratio_vs_baseline:.1f}x higher</strong> than your shift average ({shift_baseline_idle:.1f} mins).
                        </div>
                        <div style="margin-top: 0.8rem; font-size: 1rem; color: #92400e; font-weight: 800;">
                            💡 1-TAP ADVICE: Turn off engine if waiting more than 5 minutes to save fuel.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #f0fdf4; border: 3px solid #4ade80; border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem;">
                        <span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
                        <div style="font-size: 1.4rem; font-weight: 900; color: #166534; margin-top:0.3rem;">🟢 OPTIMAL IDLE PATTERN</div>
                        <div style="font-size: 1.05rem; color: #15803d; margin-top: 0.3rem;">
                            Idle time ({idle_mins:.1f} mins) is within target limits (shift avg: {shift_baseline_idle:.1f} mins).
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # SECTION 4: 🎓 TRAINING & PRE-OP HUB
        elif st.session_state.op_assistant_nav == "🎓 Training & Pre-Op Hub":
            st.markdown("## 🎓 Operator Training & Pre-Op Hub")
            st.caption("Complete your 15-item daily pre-operation walkaround checklist and practice scored scenario modules.")

            hub_tab1, hub_tab2 = st.tabs(["📋 15-Item Pre-Op Checklist", "🎓 Scored Training Simulations"])

            # REFACTORED FEATURE 3: PRE-OPERATION CHECKLIST (STEP-THROUGH FLOW)
            with hub_tab1:
                st.markdown("### 📋 Pre-Operation 15-Item Walkaround Checklist")
                
                check_bg = "#f0fdf4" if pre_op_all_clean else ("#fee2e2" if pre_op_flagged_count > 0 else "#fffbeb")
                check_border = "#22c55e" if pre_op_all_clean else ("#ef4444" if pre_op_flagged_count > 0 else "#f59e0b")
                check_title = "🟢 PRE-OPERATION CHECKLIST PASSED — SHIFT READY" if pre_op_all_clean else (f"🔴 DEFECT DETECTED ({pre_op_flagged_count} ITEM(S) FLAGGED)" if pre_op_flagged_count > 0 else f"🟡 INCOMPLETE CHECKLIST ({pre_op_passed_count}/15 PASSED)")

                st.markdown(
                    f"""
                    <div style="background-color: {check_bg}; border: 3px solid {check_border}; border-radius: 18px; padding: 1.3rem; margin-bottom: 1.2rem;">
                        <span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
                        <div style="font-size: 1.5rem; font-weight: 900; color: #0f172a; margin-top:0.3rem;">{check_title}</div>
                        <div style="font-size: 1.05rem; color: #334155; margin-top:0.3rem; font-weight: 600;">
                            Passed: <strong>{pre_op_passed_count} / {len(PRE_OP_CHECKLIST_ITEMS)}</strong> | Flagged Defects: <strong>{pre_op_flagged_count}</strong> | Safety Bonus: <strong>{'+5 Pts' if pre_op_all_clean else ('-5 Pts Defect' if pre_op_flagged_count > 0 else '0 Pts')}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                p_idx = st.session_state.active_preop_idx % len(PRE_OP_CHECKLIST_ITEMS)
                item = PRE_OP_CHECKLIST_ITEMS[p_idx]
                curr_status = st.session_state.pre_op_status.get(item["id"], "UNCHECKED")

                # Step controls
                po_c1, po_c2, po_c3 = st.columns([1, 2, 1])
                with po_c1:
                    if st.button("⬅ PREV ITEM", use_container_width=True, key="preop_step_prev"):
                        st.session_state.active_preop_idx = (p_idx - 1) % len(PRE_OP_CHECKLIST_ITEMS)
                        st.rerun()
                with po_c2:
                    st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>ITEM {p_idx + 1} OF {len(PRE_OP_CHECKLIST_ITEMS)}</div>", unsafe_allow_html=True)
                with po_c3:
                    if st.button("NEXT ITEM ➔", use_container_width=True, key="preop_step_next"):
                        st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                        st.rerun()

                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                st.progress((p_idx + 1) / len(PRE_OP_CHECKLIST_ITEMS), text=f"Step Inspection Progress: Item {p_idx + 1} of {len(PRE_OP_CHECKLIST_ITEMS)}")

                card_bg = "#f0fdf4" if curr_status == "PASSED" else ("#fee2e2" if curr_status == "ISSUE_FLAGGED" else "#f8fafc")
                card_border = "#22c55e" if curr_status == "PASSED" else ("#ef4444" if curr_status == "ISSUE_FLAGGED" else "#cbd5e1")
                cat_icon = "💧" if item["cat"] == "Fluids & Engine" else ("⚙️" if item["cat"] == "Mechanical" else ("🦺" if item["cat"] in ["Cab & Safety", "Safety Equipment"] else "⚡"))

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="background-color: {card_bg}; border: 3px solid {card_border}; border-radius: 20px; padding: 1.8rem; margin-bottom: 1.2rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;">{item['cat'].upper()}</span>
                                    <span style="font-size: 1.7rem; font-weight: 900; color: #0f172a;">{cat_icon} {p_idx+1}. {item['name']}</span>
                                </div>
                                <span style="font-size: 1.1rem; font-weight: 800; padding: 0.4rem 1.2rem; border-radius: 999px; background-color: {'#dcfce7' if curr_status=='PASSED' else ('#fee2e2' if curr_status=='ISSUE_FLAGGED' else '#f1f5f9')}; color: {'#166534' if curr_status=='PASSED' else ('#991b1b' if curr_status=='ISSUE_FLAGGED' else '#475569')};">
                                    {'🟢 PASSED' if curr_status=='PASSED' else ('🔴 DEFECT FLAGGED' if curr_status=='ISSUE_FLAGGED' else '⚪ UNCHECKED')}
                                </span>
                            </div>
                            <div style="font-size: 1.15rem; color: #475569; margin-top: 0.8rem; font-weight: 600;">
                                {item['desc']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("##### 👆 TAP ACTION (AUTO-ADVANCES TO NEXT ITEM):")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✓ PASS ITEM", use_container_width=True, key=f"step_pass_{item['id']}"):
                            st.session_state.pre_op_status[item["id"]] = "PASSED"
                            st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                            st.rerun()
                    with b2:
                        if st.button("⚠ FLAG ISSUE", use_container_width=True, key=f"step_flag_{item['id']}"):
                            st.session_state.pre_op_status[item["id"]] = "ISSUE_FLAGGED"
                            st.session_state.incident_log.insert(0, {
                                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                                "type": f"Pre-Op Defect: {item['name']}",
                                "severity": "CRITICAL",
                                "category": "HEALTH & SAFETY",
                                "impact": "-5 pts",
                                "details": f"Flagged during daily pre-op step inspection: {item['desc']}"
                            })
                            st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                            st.rerun()

                q_c1, q_c2 = st.columns(2)
                with q_c1:
                    if st.button("✅ MARK ALL 15 PASSED (QUICK START)", use_container_width=True, key="pass_all_chk"):
                        for itm in PRE_OP_CHECKLIST_ITEMS:
                            st.session_state.pre_op_status[itm["id"]] = "PASSED"
                        st.success("All 15 pre-operation checklist items marked PASSED!")
                        st.rerun()
                with q_c2:
                    if st.button("🔄 RESET CHECKLIST TO UNCHECKED", use_container_width=True, key="reset_all_chk"):
                        for itm in PRE_OP_CHECKLIST_ITEMS:
                            st.session_state.pre_op_status[itm["id"]] = "UNCHECKED"
                        st.rerun()

                with st.expander("📋 Review All 15 Items Summary", expanded=False):
                    for idx, itm in enumerate(PRE_OP_CHECKLIST_ITEMS):
                        curr_st = st.session_state.pre_op_status.get(itm["id"], "UNCHECKED")
                        st.write(f"**{idx+1}. {itm['name']}**: `{curr_st}`")

            # REFACTORED FEATURE 4: SCORED TRAINING SIMULATIONS (STEP-THROUGH ONE SCENARIO AT A TIME + WHY? EXPANDER)
            with hub_tab2:
                st.markdown("### 🎓 Scored Scenario Training Simulations")

                tot_mods = len(st.session_state.training_modules)
                passed_mods = sum(1 for m in st.session_state.training_modules if m["status"] == "Passed")
                avg_score_pct = int((passed_mods / max(1, tot_mods)) * 100)

                st.markdown(
                    f"""
                    <div style="background-color: #f0f9ff; border: 3px solid #0284c7; border-radius: 18px; padding: 1.3rem; margin-bottom: 1.2rem;">
                        <span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🎓 OPERATOR ACADEMY HISTORY</span>
                        <div style="font-size: 1.5rem; font-weight: 900; color: #0369a1; margin-top:0.3rem;">TRAINING PROGRESS: {passed_mods} / {tot_mods} MODULES PASSED ({avg_score_pct}%)</div>
                        <div style="font-size: 1.05rem; color: #0c4a6e; margin-top:0.2rem; font-weight: 600;">
                            Safety Score Impact: <strong>{'+3 Pts Bonus' if passed_mods >= 3 else 'Complete 3+ modules for +3 pts safety bonus'}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                m_idx = st.session_state.active_train_idx % tot_mods
                mod = st.session_state.training_modules[m_idx]

                # Step controls
                tc1, tc2, tc3 = st.columns([1, 2, 1])
                with tc1:
                    if st.button("⬅ PREV MODULE", use_container_width=True, key="train_step_prev"):
                        st.session_state.active_train_idx = (m_idx - 1) % tot_mods
                        st.rerun()
                with tc2:
                    st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>MODULE {m_idx + 1} OF {tot_mods}</div>", unsafe_allow_html=True)
                with tc3:
                    if st.button("NEXT MODULE ➔", use_container_width=True, key="train_step_next"):
                        st.session_state.active_train_idx = (m_idx + 1) % tot_mods
                        st.rerun()

                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

                m_status = mod["status"]
                m_border = "#22c55e" if m_status == "Passed" else ("#f59e0b" if m_status == "Needs Review" else "#cbd5e1")
                m_bg = "#f0fdf4" if m_status == "Passed" else ("#fffbeb" if m_status == "Needs Review" else "#ffffff")

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="background-color: {m_bg}; padding: 1.4rem; border-radius: 18px; border: 3px solid {m_border}; margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 1.4rem; font-weight: 900; color: #0f172a;">{mod['title']}</span>
                                <span style="background: {'#166534' if m_status=='Passed' else ('#92400e' if m_status=='Needs Review' else '#64748b')}; color: white; padding: 0.3rem 0.9rem; border-radius: 999px; font-weight: 800; font-size: 0.9rem;">
                                    {m_status.upper()}
                                </span>
                            </div>
                            <div style="font-size: 1.15rem; color: #334155; margin-top: 0.8rem; font-weight: 600;">
                                📝 <strong>Scenario:</strong> {mod['scenario']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("##### 👆 TAP YOUR DECISION OPTION:")
                    for opt_idx, opt_text in enumerate(mod["options"]):
                        is_chosen = (mod["user_answer"] == opt_idx)
                        is_correct = (opt_idx == mod["correct_idx"])

                        btn_label = f"{'✅ ' if is_chosen and is_correct else ('❌ ' if is_chosen and not is_correct else '')}{opt_text}"
                        if st.button(btn_label, key=f"mod_step_{m_idx}_opt_{opt_idx}", use_container_width=True):
                            mod["user_answer"] = opt_idx
                            if opt_idx == mod["correct_idx"]:
                                mod["status"] = "Passed"
                            else:
                                mod["status"] = "Needs Review"
                            st.rerun()

                    if mod["user_answer"] is not None:
                        if mod["user_answer"] == mod["correct_idx"]:
                            st.markdown(
                                """
                                <div style="background-color: #dcfce7; border: 2px solid #22c55e; border-radius: 14px; padding: 0.9rem 1.2rem; margin-top: 0.8rem; font-weight: 800; font-size: 1.2rem; color: #166534;">
                                    🟢 Correct! (+25 Pts)
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """
                                <div style="background-color: #fef3c7; border: 2px solid #f59e0b; border-radius: 14px; padding: 0.9rem 1.2rem; margin-top: 0.8rem; font-weight: 800; font-size: 1.2rem; color: #92400e;">
                                    🔴 Not quite — review coaching explanation below.
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        with st.expander("❓ Why? (Coaching Explanation)", expanded=False):
                            st.info(f"💡 **Coaching Explanation**: {mod['explanation']}")

        # SECTION 5: 🤖 SHIFT SUMMARY
        elif st.session_state.op_assistant_nav == "🤖 Shift Summary":
            st.markdown("## 🤖 Daily Operator AI Shift Summary")
            
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; border-radius: 16px; padding: 1.5rem;">
                        <div style="font-size: 1.6rem; font-weight: 900; color: #0f172a;">
                            📋 Shift Operational Brief & Coaching Digest
                        </div>
                        <div style="font-size: 1.1rem; color: #475569; margin-top: 0.5rem;">
                            Shift Duration: {shift_hours:.1f} Hours &nbsp;|&nbsp; Pre-Op Checklist: {'Passed' if pre_op_all_clean else 'Incomplete/Defect'} &nbsp;|&nbsp; Safety Score: <strong>{composite_safety_score}/100</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                with st.container(border=True):
                    st.markdown("#### 🌟 Shift Highlights")
                    st.write(f"• Completed 100% of stockpile loading targets in Stockpile A.")
                    st.write(f"• Maintained smooth hydraulic pump pressure (avg {current_state.hydraulics.pressure_bar:.1f} bar).")
                    st.write(f"• Finished pre-op inspection checklist ({pre_op_passed_count}/15 passed).")
            with c_s2:
                with st.container(border=True):
                    st.markdown("#### ⚠️ Focus Areas for Next Shift")
                    st.write(f"• Reduce travel speed near Zone B-4 (overspeed recorded at {speed_kmh:.1f} km/h).")
                    st.write(f"• Turn off engine during wait queues > 5 mins (idle CO₂: {wasted_fuel_l * DIESEL_CO2_PER_LITER:.1f} kg).")
                    st.write(f"• Fasten seatbelt immediately before initiating boom hyds.")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background-color: #f0fdf4; border-left: 6px solid #22c55e; padding: 1.2rem; border-radius: 12px; margin-top: 1.2rem;">
                    <span style='background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-left:0.4rem;'>🛡️ HEALTH & SAFETY</span>
                    <div style="font-size: 1.2rem; font-weight: 900; color: #166534; margin-top:0.4rem;">🌟 Supportive Operator Coaching Tip</div>
                    <div style="color: #15803d; font-size: 1.05rem; margin-top: 0.4rem; font-weight: 600;">
                        "Great digging control today, Alex! Your safety score is {composite_safety_score}/100 ({score_status}). Your smooth hydraulic application prevented high pressure surges. To reach a 98+ shift score tomorrow, keep travel speed under {STANDARD_SPEED_LIMIT} km/h and turn off the engine during 10+ minute idle waits."
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # SECTION 6: 📊 FLEET OVERVIEW (SUPERVISOR VIEW WITH AUTOMATED ESCALATIONS - UNCHANGED)
        elif st.session_state.op_assistant_nav == "📊 Fleet Overview":
            st.markdown("## 📊 VisionLink Fleet Overview (Supervisor View)")
            st.caption("Fleet-wide productivity, fuel efficiency, machine health benchmarks, and automated supervisor escalation workflow.")

            # SUPERVISOR AUTOMATED ESCALATION CONTROL CENTER
            st.markdown("### 🚨 Automated Supervisor Escalation Control Panel")

            total_esc = len(st.session_state.escalations)
            act_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Active")
            ack_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Acknowledged")
            res_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Resolved")

            esc_m1, esc_m2, esc_m3, esc_m4 = st.columns(4)
            with esc_m1:
                st.metric("Total Escalations", total_esc, delta=f"{act_esc} Active Alerts", delta_color="inverse")
            with esc_m2:
                st.metric("🔴 Active Needs Action", act_esc)
            with esc_m3:
                st.metric("🟡 Acknowledged", ack_esc)
            with esc_m4:
                st.metric("🟢 Resolved Today", res_esc)

            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

            # Interactive Supervisor Workflow Table for Escalations
            with st.container(border=True):
                st.markdown("#### 🚨 Fleet Safety & Operational Escalation Log")
                st.caption("Centralized real-time alerts automatically triggered by operator cab signals (safety score, proximity breaches, fatigue, seatbelt violations).")

                if not st.session_state.escalations:
                    st.info("🟢 No safety escalations triggered today. All machines operating normally.")
                else:
                    for esc in st.session_state.escalations[:8]:
                        st_bg = "#fee2e2" if esc["status"] == "Active" else ("#fef3c7" if esc["status"] == "Acknowledged" else "#f0fdf4")
                        st_border = "#ef4444" if esc["status"] == "Active" else ("#f59e0b" if esc["status"] == "Acknowledged" else "#22c55e")
                        st_icon = "🔴 ACTIVE" if esc["status"] == "Active" else ("🟡 ACKNOWLEDGED" if esc["status"] == "Acknowledged" else "🟢 RESOLVED")

                        st.markdown(
                            f"""
                            <div style="background-color: {st_bg}; border: 2px solid {st_border}; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                    <div>
                                        <span style="background:#1e293b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:4px; margin-right:0.5rem;">{esc['machine_id']}</span>
                                        <span style="font-size: 1.15rem; font-weight: 900; color: #0f172a;">{esc['operator']} &nbsp;|&nbsp; {esc['trigger']}</span>
                                    </div>
                                    <span style="font-weight: 800; font-size: 0.95rem; color: #0f172a;">
                                        ⏱️ {esc['time']} &nbsp;|&nbsp; <strong>{st_icon}</strong>
                                    </span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        e_btn1, e_btn2 = st.columns([1, 1])
                        with e_btn1:
                            if esc["status"] != "Acknowledged" and esc["status"] != "Resolved":
                                if st.button("👁️ ACKNOWLEDGE ALERT", key=f"ack_{esc['id']}", use_container_width=True):
                                    esc["status"] = "Acknowledged"
                                    esc["ack_time"] = "Just now"
                                    st.success(f"Escalated alert {esc['id']} marked ACKNOWLEDGED.")
                                    st.rerun()
                        with e_btn2:
                            if esc["status"] != "Resolved":
                                if st.button("✅ MARK RESOLVED", key=f"res_{esc['id']}", use_container_width=True):
                                    esc["status"] = "Resolved"
                                    esc["res_time"] = "Just now"
                                    st.success(f"Escalated alert {esc['id']} marked RESOLVED.")
                                    st.rerun()

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

            f_m1, f_m2, f_m3, f_m4 = st.columns(4)
            with f_m1:
                st.metric("Fleet Active Machines", "4 / 4", delta="100% Operational")
            with f_m2:
                st.metric("Fleet Avg Health", "89.8%", delta="-1.2%")
            with f_m3:
                st.metric("Fleet Fuel Used", "342 Liters", delta="-14 L vs target")
            with f_m4:
                st.metric("Fleet Idle Ratio", "18.5%", delta="Target < 20%")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            fleet_data = [
                {"machine": "CAT-SIM-EXC-001", "type": "Excavator", "operator": "Alex M.", "status": "🟢 NORMAL", "health": 94, "idle_pct": 14, "fuel_pct": 87},
                {"machine": "KOM-LOAD-500", "type": "Wheel Loader", "operator": "Sarah T.", "status": "🟡 WARNING", "health": 88, "idle_pct": 26, "fuel_pct": 62},
                {"machine": "VOL-HAUL-A40", "type": "Articulated Hauler", "operator": "David K.", "status": "🟢 NORMAL", "health": 98, "idle_pct": 8, "fuel_pct": 91},
                {"machine": "CAT-DOZ-D8", "type": "Dozer", "operator": "James R.", "status": "🔴 CRITICAL", "health": 79, "idle_pct": 31, "fuel_pct": 34},
            ]

            st.markdown("#### 🚜 Fleet Machine Status Grid")
            for m in fleet_data:
                with st.container(border=True):
                    fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.2, 1, 1, 1])
                    with fc1:
                        st.write(f"**{m['machine']}** ({m['type']})")
                        st.caption(f"Operator: {m['operator']}")
                    with fc2:
                        st.write(f"**Status:** {m['status']}")
                    with fc3:
                        st.write(f"**Health:** {m['health']}%")
                    with fc4:
                        st.write(f"**Idle Ratio:** {m['idle_pct']}%")
                    with fc5:
                        st.write(f"**Fuel:** {m['fuel_pct']}%")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 📈 Fleet Idle Ratio Comparison")

            fleet_df = pd.DataFrame(fleet_data)
            st.bar_chart(fleet_df.set_index("machine")["idle_pct"])
            st.info("💡 **Takeaway**: Komatsu Loader 500 and Cat Dozer D8 exceed the target 20% idle ratio threshold today.")

    st.divider()
    st.caption("Smart Operator Cab Tablet Interface | Supervised Operator Assistance Prototype")
'''

pattern = r'def render_operator_assistant_view\(.*?\):.*?(?=def render_digital_twin_view)'
match = re.search(pattern, code, flags=re.DOTALL)

if match:
    updated_code = code[:match.start()] + new_func + "\n\n" + code[match.end():]
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(updated_code)
    print("Successfully refactored render_operator_assistant_view in app.py!")
else:
    print("Pattern match failed!")
