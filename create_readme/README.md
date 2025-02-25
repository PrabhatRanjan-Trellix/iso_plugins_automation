Plugin Parameters :

	api_key(String)                                  - API key

Commands :

	1. lookup_indicators
		Lookup IP Addresses, URLs, Domains, File Hashes.At least one from domains, hashes, ip_addresses, urls is a required field.Multiple indicators can also be submitted for lookup.
		input -
			domains(String List)                           - Domains to scan.Accept valid domains only
			hashes(String List)                            - File Hashes To Query (MD5, SHA-1, SHA-256)).Accept valid hashes only
			ip_addresses(String List)                      - IP Addresses To Query.Accept valid ip-addresses only
			urls(String List)                              - URLs To Query.Accept valid urls only
			enable_raw_json(Bool)                          - Mark true to get API raw json response
			force_scan(Bool)                               - If True, plugin will automatically submit the resource for analysis if no report is found for it in VirusTotal's database.
			max_resolutions(Integer)                       - Maximum number of latest passive DNS resolutions.Accept positive integer only.Default is 10.
		output -
			vt_lookup(VTLookUp)                            - Virus Total response for Lookup Indicators
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	2. lookup_hashes
		Lookup File Hashes
		input -
			hashes(String List)                            - File Hashes To Query (MD5, SHA-1, SHA-256)).Accept valid hashes only
			enable_raw_json(Bool)                          - Mark true to get API raw json response
		output -
			hash_scan_report(HashScanReport)               - Virus Total response for Lookup hashes
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	3. lookup_ip_addresses
		Lookup IP Addresses
		input -
			ip_addresses(String List)                      - IP Addresses To Query.Accept valid ip-addresses only
			enable_raw_json(Bool)                          - Mark true to get API raw json response
		output -
			ip_scan_report(IPScanReport)                   - Virus Total response for Lookup IP Addresses
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	4. lookup_urls
		Lookup URLs
		input -
			urls(String List)                              - URLs To Query.Accept valid urls only
			enable_raw_json(Bool)                          - Mark true to get API raw json response
		output -
			url_scan_report(URLScanReport)                 - Virus Total response for Lookup urls
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	5. lookup_domains
		Lookup Domains
		input -
			domains(String List)                           - Domains to scan.Accept valid domains only
			enable_raw_json(Bool)                          - Mark true to get API raw json response
		output -
			domain_scan_report(DomainScanReport)           - Virus Total response for Lookup domains
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	6. analyse_file
		Submit file for analysis on virustotal
		input -
			file_ref(String)                               - File ref on cloud or file uuid
			enable_raw_json(Bool)                          - Mark true to get API raw json response
		output -
			file_scan_report(FileScanReport)               - Virus Total response for analyse file
			raw_json(String)                               - API response in JSON String format
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response
