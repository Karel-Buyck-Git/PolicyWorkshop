import { useState, useEffect } from "react";

export default function UserTable() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchUsers() {
      try {
        const response = await fetch("/api/users", {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch users: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        setUsers(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchUsers();

    return () => controller.abort();
  }, []);

  if (loading) {
    return <p>Loading users...</p>;
  }

  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  if (users.length === 0) {
    return <p>No users found.</p>;
  }

  const columns = Object.keys(users[0]);

  return (
    <table border="1" cellPadding="8" cellSpacing="0" style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col} style={{ textAlign: "left", background: "#f5f5f5" }}>
              {col.charAt(0).toUpperCase() + col.slice(1)}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {users.map((user, index) => (
          <tr key={user.id ?? index}>
            {columns.map((col) => (
              <td key={col}>{String(user[col] ?? "")}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
