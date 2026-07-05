import re

with open("static/app.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Login Component
login_component = """
// --- Auth Components ---
const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const res = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  return (
    <div className="flex items-center justify-center" style={{ height: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)' }}>
      <div className="card" style={{ width: '400px', padding: '2rem' }}>
        <h2 className="text-center mb-6 text-ai">PO Guardian Login</h2>
        <form onSubmit={handleSubmit} className="flex-col gap-4">
          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            required 
            style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff' }}
          />
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
            style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff' }}
          />
          {error && <div style={{ color: 'var(--status-rejected)' }}>{error}</div>}
          <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem' }}>Login</button>
        </form>
      </div>
    </div>
  );
};

"""
content = content.replace("// --- Utility Components ---", login_component + "// --- Utility Components ---")

# 2. Add custom apiFetch wrapper
api_fetch = """
const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = { ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.reload();
  }
  return response;
};
"""
content = content.replace("const API_BASE = '/api';", "const API_BASE = '/api';\n" + api_fetch)

# 3. Replace fetch with apiFetch
content = content.replace("await fetch(`${API_BASE}", "await apiFetch(`${API_BASE}")
content = content.replace("fetch(`${API_BASE}", "apiFetch(`${API_BASE}")

# Note: The login fetch inside Login component uses standard fetch intentionally because we wrote it above before doing the replace,
# Wait, replacing all `fetch(` with `apiFetch(` will also replace the one inside Login if I do it blindly.
# But I already added the Login component above, so let's fix the Login component's fetch:
content = content.replace("await apiFetch(`${API_BASE}/token`", "await fetch(`${API_BASE}/token`")

# 4. Update App to use token state
app_start = """
const App = () => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [view, setView] = useState({ name: 'dashboard', param: null });

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };
"""
content = content.replace("const App = () => {\n  const [view, setView] = useState({ name: 'dashboard', param: null });", app_start)

# Add logout button
logout_button = """
        <button className="btn btn-outline" style={{ justifyContent: 'flex-start', marginTop: 'auto', border: 'none', color: 'var(--status-rejected)' }} onClick={logout}>
          Logout
        </button>
"""
content = content.replace("</nav>", logout_button + "      </nav>")

with open("static/app.jsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated app.jsx successfully!")
