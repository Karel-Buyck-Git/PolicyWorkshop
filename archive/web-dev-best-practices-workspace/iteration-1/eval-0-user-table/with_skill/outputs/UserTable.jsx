import { useState, useEffect } from "react";

// Fetches the user list from the API and returns { users, isLoading, error }.
function useUsers() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUsers() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch("/api/users");
        if (!response.ok) {
          throw new Error(`Failed to load users (HTTP ${response.status})`);
        }
        const data = await response.json();
        if (!cancelled) {
          setUsers(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message ?? "An unexpected error occurred.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchUsers();

    // Prevent stale state updates if the component unmounts mid-request.
    return () => {
      cancelled = true;
    };
  }, []);

  return { users, isLoading, error };
}

function UserTableRow({ user }) {
  return (
    <tr>
      <td>{user.id}</td>
      <td>{user.name}</td>
      <td>{user.email}</td>
    </tr>
  );
}

function UserTableBody({ users }) {
  if (users.length === 0) {
    return (
      <tbody>
        <tr>
          <td colSpan={3}>No users found.</td>
        </tr>
      </tbody>
    );
  }

  return (
    <tbody>
      {users.map((user) => (
        <UserTableRow key={user.id} user={user} />
      ))}
    </tbody>
  );
}

export function UserTable() {
  const { users, isLoading, error } = useUsers();

  if (isLoading) {
    return <p role="status">Loading users…</p>;
  }

  if (error) {
    return (
      <p role="alert">
        Could not load users: {error}
      </p>
    );
  }

  return (
    <table aria-label="Users">
      <thead>
        <tr>
          <th scope="col">ID</th>
          <th scope="col">Name</th>
          <th scope="col">Email</th>
        </tr>
      </thead>
      <UserTableBody users={users} />
    </table>
  );
}
