import { expect, test } from "@playwright/test";

test("login screen is usable", async ({ page }) => {
  await page.goto("/login");

  await expect(page).toHaveTitle(/AccrediLens/);
  await expect(page.getByLabel("Email address")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Sign in to workspace" }),
  ).toBeVisible();
});

test("registration screen exposes required account fields", async ({ page }) => {
  await page.goto("/register");

  await expect(page.getByLabel("Full name")).toBeVisible();
  await expect(page.getByLabel("Institutional email")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Create account" }),
  ).toBeVisible();
});
