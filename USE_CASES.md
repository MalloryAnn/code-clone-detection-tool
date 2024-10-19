# Use Case #1: Running Clone Detection on a Codebase
- Actor: Developer
- Precondition: The developer has a codebase that needs to be analyzed for redundancy and has access to the Code Clone Detection Tool.
- Postcondition: The developer receives a report with identified code clones and details for refactoring.
  
<u>Steps:<u>
1.	Access the Tool: The developer opens the Code Clone Detection Tool.
2.	Load the Codebase: The developer selects the codebase that needs analysis and loads it into the tool.
3.	Configure Detection Settings: The developer adjusts detection sensitivity, setting the similarity threshold (Type cases: 70%, 90%, 100%).
4.	Run Clone Detection: The developer initiates the analysis, and the tool scans for Type 1, Type 2, and Type 3 code clones.
5.	Review Results: The developer reviews the generated report, which displays detected clones along with similarity percentages.
6.	Analyze Clones: The developer identifies the type of clones (exact, renamed, or modified) and assesses their impact on the project.
7.	Save the Report: The developer saves the report for future use or shares it with team members for further action.
 
# Use Case #2: Refactoring Based on Clone Detection Report
- Actor: Developer
- Precondition: The developer has received a clone detection report from the Code Clone Detection Tool.
- Postcondition: The developer refactors the code to remove or consolidate redundant code clones.
  
<u>Steps:<u>
1.	Review Clone Report: The developer opens the clone report generated by the tool and examines the details of detected clones.
2.	Plan Refactoring: The developer identifies redundant code blocks and formulates a refactoring strategy to eliminate the clones.
3.	Modify Code: The developer refactors the code to merge or remove the clones, ensuring the functionality remains intact.
4.	Test Refactored Code: After refactoring, the developer tests the codebase to ensure no new bugs were introduced.
5.	Rerun Clone Detection: The developer reruns the Code Clone Detection Tool to verify that the refactoring successfully removed the redundant clones.
6.	Save Updated Report: The developer saves an updated report that reflects the changes made during refactoring.
 
# Use Case #3: Using the Tool’s GUI for Clone Navigation
- Actor: Developer
- Precondition: The developer has a codebase loaded into the Code Clone Detection Tool and has run the clone detection.
- Postcondition: The developer navigates through the detected clones using the tool’s graphical interface.
  
<u>Steps:<u>
1.	Open GUI: The developer opens the tool’s graphical user interface.
2.	View Detected Clones: The detected clones are displayed in the GUI, sorted by type and similarity percentage.
3.	Filter Results: The developer uses filtering options in the GUI to focus on specific clone types (Type 1, Type 2, or Type 3) or similarity percentages (Type 1 > 90%).
4.	Navigate Through Clones: The developer clicks on individual clones to navigate to the exact location of each clone in the codebase.
5.	Flag Clones for Refactoring: The developer flags specific clones for future refactoring, based on the tool’s recommendations.
6.	Save Session: The developer saves the session, including the flagged clones and current filter settings for future work.
 