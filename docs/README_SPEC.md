# Writing AI-Readable Specifications

To ensure Axiom can accurately generate test suites, please follow these guidelines when writing your `requirements.md`:

## Structure
1.  **Title & Metadata**: Start with a clear title. Use blockquotes for metadata tags like `> [Priority: High]`.
2.  **User Story**: Standard "As a... I want... So that..." format.
3.  **Acceptance Criteria**:
    -   Use `### AC-XX: Title` for each criterion.
    -   Use **Given/When/Then** syntax (Gherkin style) to define the test steps clearly.
    -   Be explicit about HTTP methods (`GET`, `POST`) and expected status codes (`200`, `400`).
4.  **Technical Contract**: Provide JSON snippets for request/response models.

## Best Practices
-   **Ambiguity is the enemy**: Avoid words like "should work properly". Instead say "returns status 200".
-   **Edge Cases**: Explicitly define what happens on failure (e.g., AC-03 in the sample).
-   **Consistency**: Keep your header levels consistent (`##` for main sections, `###` for individual items).
