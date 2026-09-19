import '../models/job_role.dart';
import '../models/skill.dart';

// Add another JobRole here later to expand the local skill database.
const skillDatabase = <JobRole>[
  JobRole(
    name: 'Software Engineer',
    description: 'Build reliable software and solve technical problems.',
    icon: '⚙',
    requiredSkills: [
      Skill(name: 'Programming', importance: 'High'),
      Skill(name: 'Python', importance: 'Medium'),
      Skill(name: 'Java', importance: 'Medium'),
      Skill(name: 'Data Structures', importance: 'High'),
      Skill(name: 'Algorithms', importance: 'High'),
      Skill(name: 'SQL', importance: 'Medium'),
      Skill(name: 'Git', importance: 'High'),
      Skill(name: 'GitHub', importance: 'Medium'),
      Skill(name: 'OOP', importance: 'High'),
      Skill(name: 'Problem Solving', importance: 'High'),
    ],
  ),
  JobRole(
    name: 'Frontend Developer',
    description: 'Create useful, responsive experiences for the web.',
    icon: '◈',
    requiredSkills: [
      Skill(name: 'HTML', importance: 'High'),
      Skill(name: 'CSS', importance: 'High'),
      Skill(name: 'JavaScript', importance: 'High'),
      Skill(name: 'React', importance: 'High'),
      Skill(name: 'Git', importance: 'Medium'),
      Skill(name: 'Responsive Design', importance: 'High'),
      Skill(name: 'APIs', importance: 'Medium'),
    ],
  ),
  JobRole(
    name: 'Backend Developer',
    description: 'Design the services and data behind applications.',
    icon: '⌘',
    requiredSkills: [
      Skill(name: 'Python', importance: 'High'),
      Skill(name: 'Java', importance: 'Medium'),
      Skill(name: 'Node.js', importance: 'High'),
      Skill(name: 'SQL', importance: 'High'),
      Skill(name: 'REST API', importance: 'High'),
      Skill(name: 'Git', importance: 'Medium'),
      Skill(name: 'Authentication', importance: 'High'),
      Skill(name: 'Database', importance: 'High'),
    ],
  ),
  JobRole(
    name: 'Full Stack Developer',
    description: 'Connect polished interfaces to useful backend systems.',
    icon: '▣',
    requiredSkills: [
      Skill(name: 'HTML', importance: 'High'),
      Skill(name: 'CSS', importance: 'High'),
      Skill(name: 'JavaScript', importance: 'High'),
      Skill(name: 'React', importance: 'High'),
      Skill(name: 'Node.js', importance: 'High'),
      Skill(name: 'SQL', importance: 'High'),
      Skill(name: 'REST API', importance: 'High'),
      Skill(name: 'Git', importance: 'Medium'),
      Skill(name: 'GitHub', importance: 'Medium'),
    ],
  ),
  JobRole(
    name: 'Python Developer',
    description: 'Build automation, APIs, and applications with Python.',
    icon: 'Py',
    requiredSkills: [
      Skill(name: 'Python', importance: 'High'),
      Skill(name: 'OOP', importance: 'High'),
      Skill(name: 'SQL', importance: 'Medium'),
      Skill(name: 'Django', importance: 'High'),
      Skill(name: 'REST API', importance: 'High'),
      Skill(name: 'Git', importance: 'Medium'),
      Skill(name: 'Testing', importance: 'Medium'),
    ],
  ),
  JobRole(
    name: 'Java Developer',
    description: 'Create scalable systems with Java and its ecosystem.',
    icon: 'Jv',
    requiredSkills: [
      Skill(name: 'Java', importance: 'High'),
      Skill(name: 'OOP', importance: 'High'),
      Skill(name: 'SQL', importance: 'High'),
      Skill(name: 'Spring Boot', importance: 'High'),
      Skill(name: 'REST API', importance: 'Medium'),
      Skill(name: 'Git', importance: 'Medium'),
      Skill(name: 'Testing', importance: 'Medium'),
    ],
  ),
  JobRole(
    name: 'Data Analyst',
    description: 'Turn data into clear decisions and stories.',
    icon: '▥',
    requiredSkills: [
      Skill(name: 'SQL', importance: 'High'),
      Skill(name: 'Python', importance: 'High'),
      Skill(name: 'Excel', importance: 'High'),
      Skill(name: 'Statistics', importance: 'High'),
      Skill(name: 'Power BI', importance: 'Medium'),
      Skill(name: 'Data Visualization', importance: 'High'),
    ],
  ),
  JobRole(
    name: 'Data Scientist',
    description: 'Use data, experiments, and models to answer questions.',
    icon: '∑',
    requiredSkills: [
      Skill(name: 'Python', importance: 'High'),
      Skill(name: 'SQL', importance: 'Medium'),
      Skill(name: 'Statistics', importance: 'High'),
      Skill(name: 'Machine Learning', importance: 'High'),
      Skill(name: 'Pandas', importance: 'High'),
      Skill(name: 'Data Visualization', importance: 'Medium'),
    ],
  ),
];

const commonSkillNames = <String>[
  'Python', 'Java', 'HTML', 'CSS', 'JavaScript', 'SQL', 'Git', 'GitHub',
  'React', 'Node.js', 'REST API', 'Django', 'OOP', 'Testing', 'Excel',
  'Statistics', 'Pandas', 'APIs', 'Problem Solving', 'Data Structures',
];
