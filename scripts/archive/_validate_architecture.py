# -*- coding: utf-8 -*-
"""Validate cross-references in .github/ Copilot customization files."""
import os, re

base = r'D:\Git\Public_Trade_Module\.github'
issues = []

agents_dir = os.path.join(base, 'agents')
skills_dir = os.path.join(base, 'skills')
prompts_dir = os.path.join(base, 'prompts')

existing_skills = set(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else set()
existing_agents = set()
if os.path.isdir(agents_dir):
    for f in os.listdir(agents_dir):
        if f.endswith('.agent.md'):
            existing_agents.add(f.replace('.agent.md', ''))

# 1. Check for stale references to 1c-developer (old agent name)
for root, dirs, fnames in os.walk(base):
    for f in fnames:
        if f.endswith('.md') or f.endswith('.json'):
            fp = os.path.join(root, f)
            content = open(fp, 'r', encoding='utf-8').read()
            for i, line in enumerate(content.split('\n'), 1):
                # Match 1c-developer but NOT 1c-developer.agent.md in file name context
                if '1c-developer' in line:
                    rel = os.path.relpath(fp, base)
                    issues.append(f'STALE REF: {rel}:{i} -> {line.strip()[:100]}')

# 2. Check old copilot-prompts directory
if os.path.isdir(os.path.join(base, 'copilot-prompts')):
    issues.append('OLD DIR: copilot-prompts/ still exists')

# 3. Check prompts reference valid agents
valid_agents = {'orchestrator', '1c-architect', '1c-coder', '1c-form-builder', '1c-deployer'}
for f in os.listdir(prompts_dir):
    fp = os.path.join(prompts_dir, f)
    content = open(fp, 'r', encoding='utf-8').read()
    for m in re.finditer(r'agent:\s*([\w-]+)', content):
        agent_name = m.group(1)
        if agent_name not in valid_agents:
            issues.append(f'BAD AGENT REF: prompts/{f} -> agent:{agent_name}')

# 4. Check YAML frontmatter exists in agents and skills
for f in os.listdir(agents_dir):
    fp = os.path.join(agents_dir, f)
    content = open(fp, 'r', encoding='utf-8').read()
    if not content.startswith('---'):
        issues.append(f'NO FRONTMATTER: agents/{f}')

for skill_name in os.listdir(skills_dir):
    skill_file = os.path.join(skills_dir, skill_name, 'SKILL.md')
    if os.path.exists(skill_file):
        content = open(skill_file, 'r', encoding='utf-8').read()
        if not content.startswith('---'):
            issues.append(f'NO FRONTMATTER: skills/{skill_name}/SKILL.md')

# 5. Print summary
print(f'=== Architecture Validation ===')
print(f'Agents: {sorted(existing_agents)}')
print(f'Skills: {sorted(existing_skills)}')
print(f'Prompts: {sorted(os.listdir(prompts_dir))}')
print()

if issues:
    print(f'Found {len(issues)} issues:')
    for issue in issues:
        print(f'  - {issue}')
else:
    print('All references valid!')
