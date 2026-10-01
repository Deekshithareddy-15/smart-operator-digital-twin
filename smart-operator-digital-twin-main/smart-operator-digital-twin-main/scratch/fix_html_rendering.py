import re
import textwrap

app_file = r"c:\Users\91849\Downloads\smart-operator-digital-twin-main\app.py"

with open(app_file, "r", encoding="utf-8") as f:
    code = f.read()

# Function to clean st.markdown f"""...""" calls
def clean_markdown_calls(match):
    prefix = match.group(1) # e.g. st.markdown(
    content = match.group(2) # triple quoted content
    suffix = match.group(3) # e.g. , unsafe_allow_html=True)
    
    dedented_content = textwrap.dedent(content)
    return f'{prefix}"""{dedented_content}"""{suffix}'

# Let's find radar markdown specifically first
radar_old = '''            st.markdown(
                f"""
                <div style="background-color: {radar_bg}; border: 3px solid {radar_border}; border-radius: 20px; padding: 1.5rem; margin-bottom: 1.2rem;">
                    <div style="font-size: 1.3rem; font-weight: 900; text-align: center; margin-bottom: 1rem; color: #0f172a;">
                        {hazard_label}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 0.8rem; text-align: center; align-items: center;">
                        <div></div>
                        <div style="background: {'#ef4444' if hazard_dir=='FRONT' else '#e2e8f0'}; color: {'white' if hazard_dir=='FRONT' else '#475569'}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">
                            FRONT ZONE {'🔴 2.1m' if hazard_dir=='FRONT' else '🟢 CLEAR (>10m)'}
                        </div>
                        <div></div>
                        
                        <div style="background: {'#f59e0b' if hazard_dir=='LEFT' else '#e2e8f0'}; color: {'white' if hazard_dir=='LEFT' else '#475569'}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">
                            LEFT TRACK {'🟡 5.8m' if hazard_dir=='LEFT' else '🟢 CLEAR (>10m)'}
                        </div>
                        <div style="background: #1e293b; color: #f8fafc; padding: 1.2rem; border-radius: 16px; font-weight: 900; font-size: 1.1rem;">
                            🚜 MACHINE CENTER<br/><span style="font-size:0.85rem; color:#94a3b8;">CAT EXCAVATOR</span>
                        </div>
                        <div style="background: {'#f59e0b' if hazard_dir=='RIGHT' else '#e2e8f0'}; color: {'white' if hazard_dir=='RIGHT' else '#475569'}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">
                            RIGHT TRACK {'🟡 6.2m' if hazard_dir=='RIGHT' else '🟢 CLEAR (>10m)'}
                        </div>
                        
                        <div></div>
                        <div style="background: {'#ef4444' if hazard_dir=='REAR' else '#e2e8f0'}; color: {'white' if hazard_dir=='REAR' else '#475569'}; padding: 0.8rem; border-radius: 12px; font-weight: 800;">
                            REAR SWING {'🔴 2.4m DANGER' if hazard_dir=='REAR' else '🟢 CLEAR (>10m)'}
                        </div>
                        <div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )'''

radar_new = '''            front_bg = '#ef4444' if hazard_dir == 'FRONT' else '#e2e8f0'
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
                f"""<div style="background-color: {radar_bg}; border: 3px solid {radar_border}; border-radius: 20px; padding: 1.5rem; margin-bottom: 1.2rem;">
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
</div>""",
                unsafe_allow_html=True
            )'''

if radar_old in code:
    code = code.replace(radar_old, radar_new)
    print("Replaced radar HTML cleanly!")
else:
    print("Radar old pattern not matched exactly.")

with open(app_file, "w", encoding="utf-8") as f:
    f.write(code)
