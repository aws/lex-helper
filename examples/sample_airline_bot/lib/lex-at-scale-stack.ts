import * as cdk_alpha from '@aws-cdk/aws-lambda-python-alpha';
import * as cdk from 'aws-cdk-lib';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { randomUUID } from 'crypto';
export class LexAtScaleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create the fulfillment function, which will be called by the Lex bot.
    const fulfillment = fulfillmentFunction(this);

    // Create the Lex bot, its associated IAM role, and the Lex bot version and alias.
    lexbot(this, fulfillment);
  }
}


/**
 * Lexbot is a function that creates the Lex bot, its associated IAM role, and the Lex bot version and alias.
 * @param stack
 * @param fulfillment
 */
function lexbot(stack: cdk.Stack, fulfillment: cdk_alpha.PythonFunction) {
  const logGroupName = `/aws/lex/${stack.stackName.toLowerCase()}-conversation-logs`;

  const lexRole = new cdk.aws_iam.Role(stack, "LexRole", {
    assumedBy: new cdk.aws_iam.ServicePrincipal("lex.amazonaws.com"),
    roleName: `delegate-admin-lex-role-${stack.stackName.toLowerCase()}`,
    inlinePolicies: {
      "lexPolicy": new cdk.aws_iam.PolicyDocument({
        statements: [
          new cdk.aws_iam.PolicyStatement({
            actions: [
              "polly:SynthesizeSpeech",
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents",
              "lex:StartConversation",
            ],
            resources: [
              `arn:aws:logs:${stack.region}:${stack.account}:log-group:${logGroupName}`
            ]
          })
        ]
      })
    }
  });

  const lexBotExport = new cdk.aws_s3_assets.Asset(stack, "LexExportAsset", {
    path: "lex-export"
  });
  const lexBotS3Location = {
    s3Bucket: lexBotExport.s3BucketName,
    s3ObjectKey: lexBotExport.s3ObjectKey
  };
  const log_group_name = `${stack.stackName.toLowerCase()}-conversation-logs`;
  const dataProtectionPolicy = new cdk.aws_logs.DataProtectionPolicy({
    name: 'DataProtectionPolicy',
    description: 'Strip PII from logs',
    identifiers: [
      cdk.aws_logs.DataIdentifier.DRIVERSLICENSE_US,
      cdk.aws_logs.DataIdentifier.EMAILADDRESS,
      new cdk.aws_logs.CustomDataIdentifier('EmployeeId', 'EmployeeId-\\d{9}')
    ],
  });

  // Create a KMS key for encrypting the CloudWatch Logs
  const kmsKey = new cdk.aws_kms.Key(stack, 'LexLogsKmsKey', { enableKeyRotation: true });
  kmsKey.grantEncryptDecrypt(new cdk.aws_iam.ServicePrincipal(`logs.${stack.region}.amazonaws.com`))
  // Enable

  // Modify the LogGroup to use the KMS key for encryption
  const logGroup = new cdk.aws_logs.LogGroup(stack, "ConversationsLogGroup", {
    dataProtectionPolicy: dataProtectionPolicy,
    logGroupName: `/aws/lex/${log_group_name}-conversation-logs`,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
    encryptionKey: kmsKey,
  });

  const lexBot = new cdk.aws_lex.CfnBot(stack, "LexBot", {
    dataPrivacy: {
      ChildDirected: false,
    },
    idleSessionTtlInSeconds: 86400,
    roleArn: lexRole.roleArn,
    name: `${stack.stackName}`,
    autoBuildBotLocales: true,
    botFileS3Location: lexBotS3Location,
    botLocales: [
      {
        localeId: "en_US",
        nluConfidenceThreshold: 0.4
      }
    ],
    testBotAliasSettings: {
      conversationLogSettings: {
        textLogSettings: [
          {
            destination: {
              cloudWatch: {
                cloudWatchLogGroupArn: logGroup.logGroupArn,
                logPrefix: "conversation"
              }
            },
            enabled: true
          }
        ]
      },
      botAliasLocaleSettings: [
        {
          localeId: "en_US",
          botAliasLocaleSetting: {
            enabled: true,
            codeHookSpecification: {
              lambdaCodeHook: {
                codeHookInterfaceVersion: "1.0",
                lambdaArn: fulfillment.functionArn
              }
            }
          }
        }
      ]
    },

  })

  // Create random UUID
  const randomId = randomUUID();

  // Create Lex V2 Version
  const lexBotVersion = new cdk.aws_lex.CfnBotVersion(stack, `LexBotVersion${randomId}`, {
    botId: lexBot.attrId,
    description: "Lex Bot Version",
    botVersionLocaleSpecification: [
      {
        botVersionLocaleDetails: {
          sourceBotVersion: "DRAFT"
        },
        localeId: "en_US"
      }
    ]
  });

  // Create Lex V2 Bot Alias
  const lexBotAlias = new cdk.aws_lex.CfnBotAlias(stack, "LexBotAlias", {
    botAliasName: "RealAlias",
    botId: lexBot.attrId,
    botVersion: lexBotVersion.attrBotVersion,
    conversationLogSettings: {
      textLogSettings: [
        {
          destination: {
            cloudWatch: {
              cloudWatchLogGroupArn: logGroup.logGroupArn,
              logPrefix: "conversation"
            }
          },
          enabled: true
        }
      ]
    },
    botAliasLocaleSettings: [
      {
        localeId: "en_US",
        botAliasLocaleSetting: {
          enabled: true,
          codeHookSpecification: {
            lambdaCodeHook: {
              codeHookInterfaceVersion: "1.0",
              lambdaArn: fulfillment.functionArn
            }
          }
        }
      }
    ]
  });

  new cdk.CfnOutput(stack, "LexBotId", { value: lexBot.attrId });
  new cdk.CfnOutput(stack, "LexBotAliasId", { value: lexBotAlias.attrBotAliasId });
  new cdk.CfnOutput(stack, "LexBotName", { value: `${stack.stackName}LexBot` });
  new cdk.CfnOutput(stack, "LexBotAliasName", { value: "RealAlias" });

}

/**
 * Create the fulfillment Lambda function
 * @param stack The CDK stack
 * @returns The fulfillment Lambda function
 * @description This function creates the fulfillment Lambda function and its associated IAM role.  It is used to fulfill the user's intent by Lex.
 */
function fulfillmentFunction(stack: cdk.Stack): cdk_alpha.PythonFunction {
  const fulfillmentFunctionName = `fulfillment-lambda-${stack.stackName.toLocaleLowerCase()}`;
  const fulfillmentLambdaRole = new cdk.aws_iam.Role(stack, "FulfillmentLambdaRole", {
    assumedBy: new cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
    roleName: `lambda-fulfillment-role-${stack?.stackName?.toLowerCase()}`,
    inlinePolicies: {
      "lambdaPolicy": new cdk.aws_iam.PolicyDocument({
        statements: [
          new cdk.aws_iam.PolicyStatement({
            actions: [
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents"
            ],
            resources: [
              `arn:aws:logs:${stack.region}:${stack.account}:log-group:/aws/lambda/${fulfillmentFunctionName}:*`
            ]
          }),
          new cdk.aws_iam.PolicyStatement({
            actions: ["logs:CreateLogGroup"],
            resources: [`arn:aws:logs:${stack.region}:${stack.account}:log-group:/aws/lambda/${fulfillmentFunctionName}`],
            effect: cdk.aws_iam.Effect.DENY
          }),

        ]
      }),
    }
  });


  // Add suppression for wildcard permissions with evidence
  NagSuppressions.addResourceSuppressions(fulfillmentLambdaRole, [
    { id: 'AwsSolutions-IAM5', reason: 'The wildcard resource is necessary for the lambda function to create log groups dynamically.' }
  ]);


  NagSuppressions.addResourceSuppressions(fulfillmentLambdaRole, [
    { id: 'AwsSolutions-IAM4', reason: 'Not concerned about using an AWS managed policy.' }
  ]);
  // The fulfillment Lambda function itself
  const fulfillmentFunction = new cdk_alpha.PythonFunction(stack, "FulfillmentLambda", {
    entry: `lambdas/fulfillment_function/src/`,
    layers: [
      new cdk_alpha.PythonLayerVersion(stack, "FulfillmentLambdaLayer", {
        entry: "lambdas/fulfillment_function",
        compatibleRuntimes: [cdk.aws_lambda.Runtime.PYTHON_3_13],
        bundling: {
          assetExcludes: ["*.pyc", "__pycache__", '.venv', 'tests']
        }
      })
    ],
    timeout: cdk.Duration.seconds(30),
    index: `fulfillment_function/lambda_function.py`,
    runtime: cdk.aws_lambda.Runtime.PYTHON_3_13,
    insightsVersion: cdk.aws_lambda.LambdaInsightsVersion.VERSION_1_0_317_0,
    handler: "lambda_handler",
    functionName: fulfillmentFunctionName,
    tracing: cdk.aws_lambda.Tracing.ACTIVE,
    role: fulfillmentLambdaRole,
    bundling: {
      assetExcludes: ["*.pyc", "__pycache__", '.venv', 'tests']
    }
  });


  new cdk.aws_logs.LogGroup(stack, "FulfillmentLambdaLogGroup", {
    logGroupName: `/aws/lambda/${fulfillmentFunctionName}`,
    removalPolicy: cdk.RemovalPolicy.DESTROY
  });

  // Add resource-based policy statement to Lambda
  fulfillmentFunction.addPermission("LexResourcePermission", {
    action: "lambda:invokeFunction",
    principal: new cdk.aws_iam.ServicePrincipal("lexv2.amazonaws.com"),
    sourceArn: `arn:aws:lex:${stack.region}:${stack.account}:*`
  });


  return fulfillmentFunction
}
