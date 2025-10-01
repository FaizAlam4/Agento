import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:3002/api/orgs";

export default function OrgManager({ isSystemAdmin }) {
  const [orgs, setOrgs] = useState([]);
  const [form, setForm] = useState({ name: "", slug: "", description: "" });

  useEffect(() => {
    if (isSystemAdmin) {
      axios.get(API_URL).then(res => setOrgs(res.data));
    }
  }, [isSystemAdmin]);

  const handleCreate = async (e) => {
    e.preventDefault();
    const res = await axios.post(API_URL, form);
    setOrgs([...orgs, res.data]);
    setForm({ name: "", slug: "", description: "" });
  };

  const handleDelete = async (id) => {
    await axios.delete(`${API_URL}/${id}`);
    setOrgs(orgs.filter(o => o.id !== id));
  };

  if (!isSystemAdmin) return null;

  return (
    <div>
      <h2>Organizations</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: 16 }}>
        <input placeholder="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Slug" value={form.slug} onChange={e => setForm({ ...form, slug: e.target.value })} required />
        <input placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
        <button type="submit">Create</button>
      </form>
      <ul>
        {orgs.map(org => (
          <li key={org.id}>
            {org.name} ({org.slug})
            <button onClick={() => handleDelete(org.id)} style={{ marginLeft: 8 }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
