# BMAD-METHOD AI Agent Team
## Personal Finance Manager Project

**Team Configuration: Option B (4-Person Team)**  
**Framework:** BMAD-METHOD  
**Last Updated:** October 21, 2025

---

## 📁 Project Structure

```
personal-finance-app/
├── docs/
│   ├── reference.md                    # Development reference
│   └── prd.md                          # Product requirements
├── .bmad/                              # BMAD agent files
│   ├── product-owner.md                # PO/Scrum Master agent
│   ├── tech-lead.md                    # Senior Dev/Tech Lead agent
│   ├── backend-dev.md                  # Backend Developer agent
│   └── frontend-dev.md                 # Frontend/UI Developer agent
├── finance_app.py                      # Main application
├── requirements.txt                    # Python dependencies
└── README.md                           # Project overview
```

---

## 👥 Meet Your AI Agent Team

### 1. **Product Owner / Scrum Master** (`product-owner.md`)
**Role:** Product Strategy & Agile Process Manager  
**Use For:**
- Creating and updating PRD
- Writing user stories with acceptance criteria
- Prioritizing features (MoSCoW, RICE)
- Sprint planning and facilitation
- Stakeholder communication
- Success metrics analysis

**Key Commands:**
- `*create-prd` - Create Product Requirements Document
- `*create-epic` - Create epic with user stories
- `*create-story` - Write detailed user story
- `*prioritize` - Prioritize backlog items
- `*plan-sprint` - Facilitate sprint planning
- `*metrics` - Analyze product metrics

---

### 2. **Senior Developer / Tech Lead** (`tech-lead.md`)
**Role:** Technical Architecture & Quality Assurance Leader  
**Use For:**
- Architecture design decisions
- Code review and quality standards
- Testing strategy and implementation
- Performance optimization
- Security reviews
- Technical debt management
- CI/CD setup

**Key Commands:**
- `*architecture` - Design system architecture
- `*review` - Perform code review
- `*test` - Design testing strategy
- `*optimize` - Performance optimization
- `*security` - Security audit
- `*refactor` - Refactoring suggestions
- `*debug` - Debug complex issues
- `*cicd` - Setup CI/CD pipeline

---

### 3. **Full-Stack Developer (Backend)** (`backend-dev.md`)
**Role:** Backend Systems & Data Management Specialist  
**Use For:**
- Database design and queries
- Business logic implementation
- Data processing and validation
- Import/Export features (CSV, OFX, Excel)
- Repository pattern implementation
- Backend optimization

**Key Commands:**
- `*implement` - Implement backend feature
- `*database` - Design database schema
- `*query` - Write SQL queries
- `*import` - Implement import functionality
- `*export` - Implement export functionality
- `*validate` - Data validation logic
- `*optimize-db` - Optimize database
- `*migrate` - Create migrations

---

### 4. **UI/UX Developer (Frontend)** (`frontend-dev.md`)
**Role:** User Interface & Experience Specialist  
**Use For:**
- UI component implementation
- Widget design and creation
- User experience optimization
- Charts and visualizations
- Styling and theming
- Accessibility features
- Responsive design

**Key Commands:**
- `*implement-ui` - Implement UI component
- `*layout` - Design widget layout
- `*dialog` - Create dialog window
- `*widget` - Create custom widget
- `*chart` - Create data visualization
- `*style` - Apply QSS styling
- `*signals` - Connect signals/slots
- `*ux` - Improve user experience
- `*accessibility` - Add accessibility features

---

## 🚀 How to Use These Agents

### Using with Claude (Web or Desktop)

#### Method 1: Direct Upload (Recommended)
1. Open Claude.ai or Claude Desktop app
2. Start a new project for your Personal Finance Manager
3. Upload one agent file at a time when you need that expertise
4. For example: Upload `product-owner.md` when planning features

#### Method 2: Copy-Paste
1. Open the agent file you need (e.g., `backend-dev.md`)
2. Copy the entire contents
3. Paste into Claude chat
4. Claude will adopt that agent's persona

#### Method 3: Claude Projects (Best for ongoing work)
1. Create a new Project in Claude: "Personal Finance Manager"
2. Add all 4 agent files to the project knowledge base
3. Reference specific agents in your prompts:
   - "Hey @product-owner, let's create a user story for transaction import"
   - "Hey @tech-lead, review this database code"
   - "Hey @backend-dev, implement the account repository"
   - "Hey @frontend-dev, design the main window layout"

---

### Using with Other AI Tools

#### GitHub Copilot
1. Place agent files in `.github/copilot/`
2. Reference in comments: `// Using product-owner.md agent`

#### Cursor
1. Place agent files in `.cursor/rules/`
2. Use Cursor's "Chat with Rules" feature

#### Cline (VSCode Extension)
1. Configure custom instructions with agent content
2. Switch between agents as needed

#### ChatGPT (Custom GPTs)
1. Create 4 Custom GPTs, one for each agent
2. Upload corresponding markdown file as knowledge
3. Switch between GPTs based on task

---

## 💬 Example Conversations

### Planning a New Feature (Product Owner)

**You:**
```
*create-story

I need a user story for allowing users to split a single transaction 
across multiple categories (like a grocery bill that includes food, 
household items, and pet supplies).
```

**Product Owner Agent:**
```
I'll create a detailed user story for split transactions...

## US-042: Split Transactions Across Categories

**As a** meticulous expense tracker
**I want to** split a single transaction across multiple categories
**So that** I can accurately track spending in different areas from one receipt

**Priority:** P1 (Should Have)
**Story Points:** 8
**Sprint:** Sprint 5

**Acceptance Criteria:**
- [ ] Can split any transaction into 2-10 categories
- [ ] Split amounts must equal original transaction total
- [ ] Each split can have different category
- [ ] UI shows visual indicator for split transactions
- [ ] Can edit splits after creation
- [ ] Reports aggregate split amounts correctly

... [full user story]
```

---

### Implementing Backend (Backend Developer)

**You:**
```
*implement

Implement the repository pattern for the Account model with CRUD operations.
Include proper transaction handling and validation.
```

**Backend Developer Agent:**
```
I'll implement a comprehensive AccountRepository with proper 
transaction handling and validation...

[Provides complete implementation with:
- Full CRUD methods
- Transaction boundaries
- Validation logic
- Error handling
- Unit test examples]
```

---

### Code Review (Tech Lead)

**You:**
```
*review

[paste code here]

Please review this transaction import function. Looking for:
- Performance issues
- Security concerns
- Best practices
```

**Tech Lead Agent:**
```
I'll perform a comprehensive code review...

## Code Review: Transaction Import Function

### Summary
Overall solid implementation with a few concerns around error 
handling and performance.

### Issues Found:

**🔴 High Priority:**
1. **Line 45**: SQL injection vulnerability - using string 
   formatting instead of parameterized queries
   
**🟡 Medium Priority:**
2. **Line 78**: Individual inserts in loop - should use batch 
   operations for better performance
   
**🟢 Low Priority:**
3. **Line 102**: Magic number - extract to constant

### Recommendations:
[Detailed suggestions with code examples]
```

---

### Building UI (Frontend Developer)

**You:**
```
*implement-ui

Create a dialog for adding recurring transactions with:
- Frequency selection (daily, weekly, monthly, yearly)
- Start and optional end date
- All the usual transaction fields
- Preview of next 3 occurrences
```

**Frontend Developer Agent:**
```
I'll create a comprehensive RecurringTransactionDialog with all 
requested features...

[Provides complete implementation with:
- Full Qt dialog code
- Layout design
- Signal/slot connections
- Validation logic
- Preview feature
- Styling]
```

---

## 🎯 Workflow Examples

### Feature Development Flow

1. **Planning Phase** (Product Owner)
   ```
   *create-epic
   [Describe feature: Budget tracking and alerts]
   
   Output: Epic with multiple user stories
   ```

2. **Architecture Design** (Tech Lead)
   ```
   *architecture
   [Review epic and design database schema + components]
   
   Output: Architecture document with diagrams
   ```

3. **Backend Implementation** (Backend Developer)
   ```
   *implement
   [Implement budget repository and business logic]
   
   Output: Complete backend code with tests
   ```

4. **Frontend Implementation** (Frontend Developer)
   ```
   *implement-ui
   [Create budget management UI]
   
   Output: Complete UI components
   ```

5. **Code Review** (Tech Lead)
   ```
   *review
   [Review all code from backend and frontend]
   
   Output: Review feedback and improvement suggestions
   ```

6. **Sprint Retrospective** (Product Owner)
   ```
   *retro
   [Facilitate retrospective discussion]
   
   Output: Retrospective summary with action items
   ```

---

## ⚙️ Agent Configuration

Each agent has embedded YAML configuration that defines:

```yaml
agent:
  id: "agent-id"
  role: "Role Title"
  expertise: [list of skills]
  commands: [available commands]
  dependencies: [templates, tasks, data files]
  configuration: [project-specific settings]
```

You can customize:
- Commands and triggers
- Expertise areas
- Personality and communication style
- Project-specific configuration

---

## 🔄 Agent Switching Tips

**When to use each agent:**

- **Product Owner**: When you need to decide WHAT to build
- **Tech Lead**: When you need to decide HOW to build (architecture)
- **Backend Developer**: When writing data/logic code
- **Frontend Developer**: When building UI components

**Pro Tip:** You can have multiple conversations open:
- Tab 1: Product Owner (planning)
- Tab 2: Tech Lead (reviewing)
- Tab 3: Backend Dev (implementing)
- Tab 4: Frontend Dev (building UI)

---

## 📚 Additional Resources

### BMAD-METHOD Documentation
- GitHub: https://github.com/bmad-code-org/BMAD-METHOD
- User Guide: https://bmadcodes.com/user-guide/
- Discord Community: https://discord.gg/gk8jAdXWmj

### Project Documentation
- `docs/reference.md` - Complete technical reference
- `docs/prd.md` - Product requirements and roadmap
- `README.md` - Project overview and setup

### Learning Resources
- PySide6 Docs: https://doc.qt.io/qtforpython-6/
- Python Testing: https://docs.pytest.org/
- BMAD Examples: https://medium.com/@visrow

---

## 🎓 Best Practices

### 1. **Start with the Right Agent**
- Planning features? → Product Owner
- Technical decisions? → Tech Lead
- Building backend? → Backend Developer
- Creating UI? → Frontend Developer

### 2. **Use Commands**
- Agents have specific commands (e.g., `*implement`, `*review`)
- Commands help agents understand exactly what you need
- Type `*help` to any agent to see all available commands

### 3. **Provide Context**
- Reference user stories when implementing
- Share code when asking for reviews
- Include requirements when designing

### 4. **Iterate**
- Agents can refine their output based on feedback
- Ask follow-up questions
- Request alternative approaches

### 5. **Document Decisions**
- Keep agent outputs in your project documentation
- Technical decisions from Tech Lead → docs/adr/
- User stories from Product Owner → docs/stories/
- Architecture diagrams → docs/architecture/

---

## 🤝 Team Collaboration Flow

```
┌─────────────────┐
│  Product Owner  │ Creates user stories and prioritizes
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Tech Lead     │ Reviews feasibility, designs architecture
└────────┬────────┘
         │
         ├──────────────────────┐
         ↓                      ↓
┌─────────────────┐    ┌─────────────────┐
│  Backend Dev    │    │  Frontend Dev   │ Implement features
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ↓
         ┌─────────────────┐
         │   Tech Lead     │ Reviews and validates
         └─────────────────┘
```

---

## 🚨 Troubleshooting

### Agent not following role?
- Make sure you uploaded/pasted the entire agent file
- Try starting message with agent's command (e.g., `*implement`)

### Need different expertise?
- Customize agent YAML configuration
- Add new commands to triggers array
- Adjust expertise list

### Agent responses too verbose?
- Ask agent to be more concise
- Request only code without explanations
- Use specific commands rather than free-form questions

### Want to combine agents?
- Use sequential approach (one after another)
- Or create a "team discussion" by referencing previous agent outputs

---

## 📞 Getting Help

- **BMAD Discord**: https://discord.gg/gk8jAdXWmj
- **GitHub Issues**: https://github.com/bmad-code-org/BMAD-METHOD/issues
- **Documentation**: https://bmadcodes.com/

---

## 🎉 Ready to Build!

You now have a complete AI development team ready to help you build your Personal Finance Manager application. Each agent brings specialized expertise and is ready to assist at every stage of development.

**Quick Start:**
1. Upload `product-owner.md` to Claude
2. Ask: "*create-prd for personal finance app"
3. Review and refine the PRD
4. Switch to other agents as you progress through development

Happy building! 🚀

---

*AI Agent Team Version: 1.0.0*  
*BMAD-METHOD Framework*  
*Personal Finance Manager Project*  
*Created: October 21, 2025*