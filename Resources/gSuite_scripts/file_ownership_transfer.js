// ** CONFIGURATION **
// -------------------
const TARGET_FOLDER_ID = 'gDrive folder ID'; 
// The ID of the main shared folder to start scanning from.

const RECIPIENT_EMAIL = 'EMAIL ADDRESS OF THE MAIN'; 
// The email address of the person who should receive the ownership request.

const TIME_THRESHOLD_MINUTES = 10;
// Defines how far back (in minutes) the script looks for files created/uploaded.

// -------------------

/**
 * Main function initiated by the time-driven trigger.
 * It sets up the scanning parameters and starts the recursive search.
 */
function initiateOwnershipTransferRequests() {
  const rootFolder = DriveApp.getFolderById(TARGET_FOLDER_ID);
  
  const now = new Date().getTime();
  const thresholdTime = now - (TIME_THRESHOLD_MINUTES * 60 * 1000); 
  
  const stats = {
    foldersScanned: 0,
    totalFilesChecked: 0,
    newFilesProcessed: 0,
    thresholdTime: thresholdTime,
    currentOwnerEmail: Session.getActiveUser().getEmail()
  };
  
  Logger.log('================================================================');
  Logger.log(`STARTING SCAN - ${new Date().toLocaleString()}`);
  Logger.log(`Scanning for new files since ${new Date(thresholdTime).toLocaleString()} (${TIME_THRESHOLD_MINUTES} minutes ago)`);
  Logger.log(`Script Owner/Uploader Email: ${stats.currentOwnerEmail}`);
  Logger.log(`Recipient Email: ${RECIPIENT_EMAIL}`);
  Logger.log('================================================================');
  
  // Start the recursive process from the root folder
  processFolder(rootFolder, stats);
  
  Logger.log('================================================================');
  Logger.log('--- SCAN SUMMARY ---');
  Logger.log(`Total Folders Scanned: ${stats.foldersScanned}`);
  Logger.log(`Total Files Checked (at all levels): ${stats.totalFilesChecked}`);
  Logger.log(`Ownership Requests Initiated (New Files): ${stats.newFilesProcessed}`);
  Logger.log('SCAN COMPLETE.');
  Logger.log('================================================================');
}


/**
 * Recursively checks a folder and all its subfolders for new files 
 * and attempts to initiate the ownership transfer request using the Advanced Drive Service.
 * 
 * @param {GoogleAppsScript.Drive.Folder} folder The folder object to scan.
 * @param {Object} stats The statistics object to track progress.
 */
function processFolder(folder, stats) {
  stats.foldersScanned++;
  
  Logger.log(`--- SCANNING FOLDER: ${folder.getName()} (ID: ${folder.getId()}) ---`);
  
  const cache = CacheService.getScriptCache();
  const currentOwnerEmail = stats.currentOwnerEmail;

  // 1. Process files in the current folder (top level of the recursion)
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    const fileId = file.getId();
    stats.totalFilesChecked++;

    // Use getDateCreated() to catch recent uploads
    const isNew = file.getDateCreated().getTime() > stats.thresholdTime; 
    const isOwnedByMe = file.getOwner().getEmail() === currentOwnerEmail;

    if (cache.get(fileId)) {
      Logger.log(` File ${file.getName()} (${fileId}) skipped (Already Processed/Cached).`);
      continue;
    }
    
    if (isNew && isOwnedByMe) {
      
      Logger.log(` NEW FILE FOUND: ${file.getName()}. Created on: ${file.getDateCreated().toLocaleString()} Attempting ownership transfer request via Drive API...`); 
      stats.newFilesProcessed++;

      try {
        // Step 1: Find the permission ID for the recipient
        let permissionListResponse = Drive.Permissions.list(fileId);
        let permissions = permissionListResponse.items ||[]; 

        let permissionId = permissions.find(p => p.emailAddress === RECIPIENT_EMAIL)?.id;

        // If permission ID is not found, we use the Advanced API to create it.
        if (!permissionId) {
            
            // CRITICAL FIX: Use Drive API's Permissions.create
            const newPermissionResource = {
                role: 'writer', // Must be 'writer' to allow ownership transfer
                type: 'user',
                emailAddress: RECIPIENT_EMAIL,
            };
            
            // FIX: Add sendNotificationEmails: true to the CREATE call
            const createdPermission = Drive.Permissions.create(newPermissionResource, fileId, {
                sendNotificationEmails: true 
            });
            permissionId = createdPermission.id;

            Logger.log(` Recipient permission created via API (ID: ${permissionId}). Proceeding...`);
        }

        // Step 2: Initiate the ownership transfer request using the Advanced Drive API.
        if (permissionId) {
            const resource = {
                role: 'writer', 
                pendingOwner: true // The flag that triggers the recipient's email invitation
            };
            
            // FIX: Add sendNotificationEmails: true to the UPDATE call
            Drive.Permissions.update(resource, fileId, permissionId, {
                sendNotificationEmails: true
            });

            // 3. Mark the file as processed IN THE SUCCESS PATH ONLY
            cache.put(fileId, 'processed', 3600); // Cache for 1 hour
            
            Logger.log(` SUCCESS: Ownership request for ${file.getName()} (ID: ${fileId}) initiated. Recipient must accept.`);
        } else {
             Logger.log(` FAILED: FATAL - Permission ID could not be established after attempting creation.`);
             // NO CACHE UPDATE: File will be retried on next run.
        }

      } catch (e) {
        // Log API errors, but DO NOT update the cache. File will be retried.
        Logger.log(` API ERROR during transfer initiation for ${file.getName()}: ${e.toString()}`);
        
      } 
    } else {
        let skipReason =[]; 
        if (!isNew) {
          skipReason.push(`Not recently uploaded (Created: ${file.getDateCreated().toLocaleString()}).`);
        }
        if (!isOwnedByMe) {
          skipReason.push(`Not owned by current user (Owned by: ${file.getOwner().getEmail()}).`);
        }
        Logger.log(` File ${file.getName()} skipped. Reason: ${skipReason.join(" / ")}`);
    }
  }

  // 2. Recurse into all subfolders
  const subFolders = folder.getFolders();
  while (subFolders.hasNext()) {
    const subFolder = subFolders.next();
    processFolder(subFolder, stats);
  }
}