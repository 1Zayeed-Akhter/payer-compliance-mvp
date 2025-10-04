# Changelog

## [v2.0.0] - 2024-01-XX - Audit Workflow Evolution

### Added
- **Streamlit Theme**: Added `.streamlit/config.toml` with professional teal theme
- **Database Layer**: New `db.py` with SQLite helpers for claims and attestations tracking
- **Tabbed UI**: Converted single-page app to 3-tab structure:
  - 📁 Upload Claims: File upload and compliance checking
  - 🔍 Compliance Review: Results display and downloads
  - 📋 Attestation Dashboard: Database-driven attestation tracking
- **Database Persistence**: Flagged claims automatically saved to database after processing
- **Attestation Tracking**: Support for Pending/Signed/Verified status workflow

### Database Schema
- **claims table**: Stores claim data with compliance issues
- **attestations table**: Tracks attestation status and timestamps
- **Automatic linking**: Claims with issues automatically create attestation records

### Enhanced Features
- **Professional UI**: Teal color scheme with improved typography
- **Audit Trail**: Database persistence for compliance tracking
- **Status Dashboard**: Overview of attestation workflow progress
- **Filtering Support**: Database queries support provider, status, and issue filtering

### Preserved Functionality
- ✅ CSV export with flagged claims only
- ✅ ZIP attestation PDF generation
- ✅ All existing compliance rules and checks
- ✅ Sample data generation
- ✅ HIPAA disclaimers and demo warnings

### Technical Improvements
- **Modular Design**: Separated concerns into focused tab functions
- **Database Integration**: SQLite backend for persistent audit workflow
- **Error Handling**: Graceful handling of database and UI errors
- **Code Organization**: Clean separation between UI, business logic, and data layers

### Breaking Changes
- **UI Structure**: App now uses tabs instead of single-page layout
- **Database Dependency**: Requires SQLite for full functionality
- **Session State**: Results persist across tab navigation

### Migration Notes
- Existing CSV upload and compliance checking workflows remain unchanged
- Database is automatically initialized on first run
- No data migration required for existing functionality

## [v2.1.0] - 2024-01-XX - Interactive Attestation Workflow

### Added
- **Interactive Dashboard**: Per-row actions for attestation management
- **Attestation Modal**: Professional signature capture interface with:
  - Complete claim details display
  - Compliance issues listed as bullets
  - Exact attestation statement as specified
  - Required checkbox validation
  - Electronic signature capture with name input
  - UTC timestamp recording
- **Verification Workflow**: Admin-side verification action for signed attestations
- **Reminder System**: Automated reminders for pending attestations > 48 hours
- **Advanced Filtering**: 
  - Provider dropdown filter
  - Status multi-select filter  
  - Issue text search
- **Enhanced UX**: 
  - Summary counters for all status types
  - Expandable claim rows with actions
  - Real-time status updates with st.rerun()
  - Success toasts and notifications

### Enhanced Features
- **Signature Recording**: "Electronically signed by <name> on <UTC ISO timestamp>" format
- **Status Transitions**: Pending → Signed → Verified workflow
- **Reminder Logic**: Smart 48-hour reminder system with console logging
- **Filter Persistence**: Maintains filter state during session
- **Action Validation**: Prevents invalid state transitions

### Technical Improvements
- **Modal Management**: Session state-based modal system
- **Database Integration**: Seamless status updates with proper timestamps
- **Error Handling**: Graceful handling of invalid signatures and states
- **Performance**: Efficient filtering and querying of large datasets

### UX Enhancements
- **Visual Indicators**: Clear status badges and action buttons
- **Responsive Design**: Proper column layouts for different screen sizes
- **User Feedback**: Immediate confirmation of actions with success messages
- **Accessibility**: Clear labeling and intuitive navigation

## [v2.1.1] - 2024-01-XX - Bug Fixes

### Fixed
- **Duplicate Key Error**: Fixed "multiple elements with the same key" error in attestation dashboard
- **Claim Counting Issue**: Resolved incorrect claim count (28 vs 14) by preventing duplicate attestation records
- **Duplicate Claims**: Fixed issue where Dr. Rodriguez claims couldn't open attestations due to duplicate claim IDs
- **Database Query**: Improved query to return only the most recent attestation per claim

### Technical Improvements
- **Unique Key Generation**: Uses `claim_id + row_index` for unique Streamlit component keys
- **Duplicate Prevention**: Enhanced database queries to prevent duplicate attestation records
- **Debug Information**: Added temporary debug panel to troubleshoot data issues
- **Query Optimization**: Uses ROW_NUMBER() window function to select most recent attestations

### Database Changes
- **Attestation Insert**: Modified to use `WHERE NOT EXISTS` to prevent duplicate attestation records
- **List Query**: Updated to use window function for selecting most recent attestation per claim
- **Data Integrity**: Ensures one-to-one relationship between claims and attestations
