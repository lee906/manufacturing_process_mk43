const Navbar = () => {  
  return (
    <div className="navbar navbar-expand-md d-print-none">
      <div className="container-fluid">
        <ul className="navbar-nav">
          <li className="nav-item">
            <span className="nav-link">
              <i className="ti ti-thermometer me-1"></i>
              <span>날씨:</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#FF6F00" className="icon icon-tabler icons-tabler-filled icon-tabler-sun">
                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                <path d="M12 19a1 1 0 0 1 .993 .883l.007 .117v1a1 1 0 0 1 -1.993 .117l-.007 -.117v-1a1 1 0 0 1 1 -1z" />
                <path d="M18.313 16.91l.094 .083l.7 .7a1 1 0 0 1 -1.32 1.497l-.094 -.083l-.7 -.7a1 1 0 0 1 1.218 -1.567l.102 .07z" />
                <path d="M7.007 16.993a1 1 0 0 1 .083 1.32l-.083 .094l-.7 .7a1 1 0 0 1 -1.497 -1.32l.083 -.094l.7 -.7a1 1 0 0 1 1.414 0z" />
                <path d="M4 11a1 1 0 0 1 .117 1.993l-.117 .007h-1a1 1 0 0 1 -.117 -1.993l.117 -.007h1z" />
                <path d="M21 11a1 1 0 0 1 .117 1.993l-.117 .007h-1a1 1 0 0 1 -.117 -1.993l.117 -.007h1z" />
                <path d="M6.213 4.81l.094 .083l.7 .7a1 1 0 0 1 -1.32 1.497l-.094 -.083l-.7 -.7a1 1 0 0 1 1.217 -1.567l.102 .07z" />
                <path d="M19.107 4.893a1 1 0 0 1 .083 1.32l-.083 .094l-.7 .7a1 1 0 0 1 -1.497 -1.32l.083 -.094l.7 -.7a1 1 0 0 1 1.414 0z" />
                <path d="M12 2a1 1 0 0 1 .993 .883l.007 .117v1a1 1 0 0 1 -1.993 .117l-.007 -.117v-1a1 1 0 0 1 1 -1z" />
                <path d="M12 7a5 5 0 1 1 -4.995 5.217l-.005 -.217l.005 -.217a5 5 0 0 1 4.995 -4.783z" />
              </svg>
            </span>
          </li>
          <li className="nav-item ms-3">
            <span className="nav-link">
              <i className="ti ti-droplet me-1"></i>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="url(#tempGradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <defs>
                  <linearGradient id="tempGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#FF6B6B"/>
                    <stop offset="50%" stopColor="#FFA94D"/>
                    <stop offset="100%" stopColor="#4DABF7"/>
                  </linearGradient>
                </defs>
                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                <path d="M10 13.5a4 4 0 1 0 4 0v-8.5a2 2 0 0 0 -4 0v8.5" />
                <path d="M10 9l4 0" />
              </svg>
              <span>온도: 25</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="icon icon-tabler icons-tabler-outline icon-tabler-temperature-celsius">
                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                <path d="M6 8m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
                <path d="M20 9a3 3 0 0 0 -3 -3h-1a3 3 0 0 0 -3 3v6a3 3 0 0 0 3 3h1a3 3 0 0 0 3 -3" />
              </svg>
            </span>
          </li>
          <li className="nav-item ms-3">
            <span className="nav-link">
              <i className="ti ti-droplet me-1"></i>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#3fa9f5"
                className="icon icon-tabler icons-tabler-filled icon-tabler-droplet">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M10.708 2.372a2.382 2.382 0 0 0 -.71 .686l-4.892 7.26c-1.981 3.314 -1.22 7.466 1.767 9.882c2.969 2.402 7.286 2.402 10.254 0c2.987 -2.416 3.748 -6.569 1.795 -9.836l-4.919 -7.306c-.722 -1.075 -2.192 -1.376 -3.295 -.686z" />
              </svg>
              <span>습도: 55%</span>
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Navbar;