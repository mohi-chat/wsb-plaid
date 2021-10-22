import React, { useContext } from "react";
import Callout from "plaid-threads/Callout";
import Button from "plaid-threads/Button";
import InlineLink from "plaid-threads/InlineLink";

import Link from "../Link";
import Context from "../../Context";

import styles from "./index.module.scss";

const Header = () => {
  const {
    itemId,
    accessToken,
    linkToken,
    linkSuccess,
    isItemAccess,
    backend,
    linkTokenError,
  } = useContext(Context);

  const [email, setEmail] = React.useState(localStorage.getItem("email") || "");
  const isAccessAuthorized = (email.length==0? false : true); 

  return (
    <div className={styles.grid}>
      {
        !isAccessAuthorized ? (
          <>
            <h3>404: Page Not Found</h3>
            <p>Oops. Our servers didn't recognize the page you were looking for. Please try again after some time.</p>
          </>
        ) : (
          <>
            {!linkSuccess ? (
              <>
                <h3 className={styles.title}>Integrate your account with WSB!</h3>
                <p className={styles.introPar}>
                  Follow the link to connect your trading accounts to WSB.
                  Please don't press the back or refresh button once linking is in progress.
                </p>
                {/* message if backend is not running and there is no link token */}
                {!backend ? (
                  <Callout warning>
                    Unable to fetch link_token: please make sure your backend server
                    is running and that your .env file has been configured with your
                    <code>PLAID_CLIENT_ID</code> and <code>PLAID_SECRET</code>.
                  </Callout>
                ) : /* message if backend is running and there is no link token */
                linkToken == null && backend ? (
                  <Callout warning>
                    <div>
                      Unable to fetch link_token: We are working on this. Please try again later.
                      correctly.
                    </div>
                    <div>
                      Error Code: <code>{linkTokenError.error_code}</code>
                    </div>
                    <div>
                      Error Type: <code>{linkTokenError.error_type}</code>{" "}
                    </div>
                    <div>Error Message: {linkTokenError.error_message}</div>
                  </Callout>
                ) : linkToken === "" ? (
                  <div className={styles.linkButton}>
                    <Button large disabled>
                      Loading...
                    </Button>
                  </div>
                ) : (
                  <div className={styles.linkButton}>
                    <Link />
                  </div>
                )}
              </>
            ) : (
              <>
                {isItemAccess ? (
                  <div>
                  <h3 className={styles.title}>Account linked</h3>
                  <h4 className={styles.subtitle}>
                    Congrats! You have successfully linked your account with WSB. It can take upto 2 minutes to sync with your brokerage account. You may now return to App.
                  </h4>
                  </div>
                ) : (
                  <h4 className={styles.subtitle}>
                    <Callout warning>
                      Unable to create an item. We are working on this. Please try again later.
                    </Callout>
                  </h4>
                )}
              </>
            )}
          </>
        )
      }
    </div>
  );
};

Header.displayName = "Header";

export default Header;
