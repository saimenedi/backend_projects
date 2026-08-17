const { error } = require("console");
const https = require("https");
const process = require("process");

const username = process.argv[2];

if (!username) {
  console.error("Error: Please provide a GitHub username");
  console.error("Usage: github-activity <username>");
  process.exit(1);
}

//function to make HTTPS request
function fetchGitHubActivity(username) {
  return new Promise((resolve, reject) => {
    const url = `https://api.github.com/users/${username}/events`;

    const options = {
      headers: {
        "User-Agent": "Node.js-GitHub-Activity-CLI",
        Accept: "application/vnd.github.v3+json",
      },
    };
    https
      .get(url, options, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          if (res.statusCode === 200) {
            try {
              const events = JSON.parse(data);
              resolve(events);
            } catch (error) {
              reject(new Error("Failed to parse API response"));
            }
          } else if (res.statusCode === 400) {
            reject(new Error(`User '${username}' not found`));
          } else if (res.statusCode === 403) {
            reject(
              new Error("API rate limit exceeded. Please try again later."),
            );
          } else {
            reject(new Error(`Network error: ${error.message}`));
          }
        });
      })
      .on("error", (error) => {
        reject(new Error(`Network error: ${error.message}`));
      });
  });
}
// function to format timestamp

function formatTimestamp(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMind}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// Function to format activity events

function formatActivity(events) {
  if (!events || events.length === 0) {
    return "No recent activity found.";
  }

  const formattedActivities = events.slice(0, 10).map((event) => {
    const type = event.type;
    const repo = event.repo.name;
    const timestamp = formatTimestamp(event.created_at);
    let description;

    switch (type) {
      case "PushEvent":
        const commitCount =
          event.payload.commits?.length || event.payload.size || 1;
        description = `Pushed ${commitCount} commit${commitCount > 1 ? "s" : ""} to ${repo}`;
        break;
      case "IssuesEvent":
        description = `Opened a new issue in ${repo}`;
        break;
      case "PullRequestEvent":
        description = `Opened a new pull request in ${repo}`;
        break;
      case "WatchEvent":
        description = `Started ${repo}`;
        break;
      case "ForkEvent":
        description = `Forked ${repo}`;
        break;
      case "CreateEvent":
        description = `Created a new repository or branch in ${repo}`;
        break;
      case "DeleteEvent":
        description = `Deleted a repository or branch in ${repo}`;
        break;
      case "ReleaseEvent":
        description = `Released a new version in ${repo}`;
        break;
      case "GollumEvent":
        description = `Updated wiki pages in ${repo}`;
        break;
      default:
        description = `Performed ${type} in ${repo}`;
    }
    return `[${timestamp}] ${description}`;
  });

  return formattedActivities.join("\n- ");
}

// Main execution
async function main() {
  try {
    console.log(`Fetching recent activity for ${username}...\n`);
    const events = await fetchGitHubActivity(username);
    const activity = formatActivity(events);

    console.log("Recent Activity:");
    console.log("- " + activity);
    console.log("\n");
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
