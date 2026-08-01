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

// Function to format activity events

function formatActivity(events) {
  if (!events || events.length === 0) {
    return "No recent activity found.";
  }
  const formattedActivities = events.slice(0, 10).map((event) => {
    const type = event.type;
    const repo = event.repo.name;

    switch (type) {
      case "PushEvent":
        return `Pushed ${event.payload.size || event.payload.commits?.length || 1}
                commit${event.payload.size > 1 ? "s" : ""} to ${repo}`;
      case "IssuesEvent":
        return `Opened a new issue in ${repo}`;
      case "PullRequestEvent":
        return `Opened a new pull request in ${repo}`;
      case "WatchEvent":
        return `Started ${repo}`;
      case "ForkEvent":
        return `Forked ${repo}`;
      case "CreateEvent":
        return `Created a new repository or branch in ${repo}`;
      case "DeleteEvent":
        return `Deleted a repository or branch in ${repo}`;
      case "ReleaseEvent":
        return `Released a new version in ${repo}`;
      case "GollumEvent":
        return `Updated wiki pages in ${repo}`;
      default:
        return `Performed ${type} in ${repo}`;
    }
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
